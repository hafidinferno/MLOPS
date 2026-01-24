import pickle
import pandas as pd
import numpy as np
import os
import logging
import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Configuration Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Fraud Detection API", version="2.0")

# Global Artifacts
artifacts = {
    "model": None,
    "pca": None,
    "preprocessor": None
}

# Configuration
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://n8n:5678/webhook/fraud-alert")
FRAUD_THRESHOLD = 0.7
RETRAIN_THRESHOLD = 100 # Nombre de nouvelles données avant retrain

@app.on_event("startup")
async def load_artifacts():
    """Charge les modèles et préprocesseurs au démarrage."""
    try:
        artifact_path = os.getenv("ARTIFACT_PATH", "/artifacts")
        
        with open(os.path.join(artifact_path, 'model.pickle'), 'rb') as f:
            artifacts["model"] = pickle.load(f)
            
        with open(os.path.join(artifact_path, 'pca.pickle'), 'rb') as f:
            artifacts["pca"] = pickle.load(f)
            
        with open(os.path.join(artifact_path, 'preprocessor.pickle'), 'rb') as f:
            artifacts["preprocessor"] = pickle.load(f)
            
        logger.info("Artefacts chargés avec succès.")
    except Exception as e:
        logger.error(f"Erreur fatal au chargement des artefacts: {e}")
        # On ne crash pas l'app, mais les prédictions échoueront
        
class TransactionInput(BaseModel):
    merchant_category: str
    merchant_type: str
    amount: float
    currency: str
    country: str
    city_size: str
    card_type: str
    card_present: bool
    device: str
    channel: str
    distance_from_home: float
    high_risk_merchant: bool
    transaction_hour: int
    weekend_transaction: bool
    email: Optional[str] = None

class FeedbackInput(BaseModel):
    payload: Dict[str, Any]
    correct_class: bool # True = Fraud, False = Legit
    prediction: bool

def process_features(data: dict):
    """Transforme les données brutes en vecteurs PCA."""
    if not all(artifacts.values()):
        raise ValueError("Modèles non chargés.")
        
    df = pd.DataFrame([data])
    
    # Preprocess
    X_processed = artifacts["preprocessor"].transform(df)
    
    # PCA
    X_pca = artifacts["pca"].transform(X_processed)
    
    return X_pca

async def trigger_fraud_alert(transaction_data: dict, probability: float):
    """Envoie une alerte à n8n en arrière-plan."""
    try:
        payload = {
            "transaction": transaction_data,
            "probability": probability,
            "alert_time": pd.Timestamp.now().isoformat()
        }
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=5)
        logger.info(f"Alerte envoyée à n8n. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Echec de l'envoi vers n8n: {e}")

async def check_and_retrain():
    """Vérifie si on doit réentraîner (Simulation)."""
    # Logique simplifiée pour ne pas bloquer l'API
    # Dans un vrai système, cela serait fait par un job séparé (Airflow/Cron)
    file_path = '/data/prod_data.csv'
    if os.path.exists(file_path):
        # On compte juste les lignes pour l'exemple
        with open(file_path) as f:
            count = sum(1 for _ in f) - 1
        
        if count % RETRAIN_THRESHOLD == 0:
            logger.info(f"Seuil de réentraînement atteint ({count}). Triggering Retraining Job...")
            # Ici on pourrait lancer le script train_model.py via subprocess
            # ou envoyer un signal à un orchestrateur.
    
@app.get("/health")
def health_check():
    return {"status": "ok", "artifacts_loaded": all(artifacts.values())}

@app.post("/predict")
async def predict(transaction: TransactionInput, background_tasks: BackgroundTasks):
    if not all(artifacts.values()):
        raise HTTPException(status_code=503, detail="Service Unavailable: Models not loaded")
    
    try:
        data = transaction.dict()
        X_pca = process_features(data)
        
        # Predict
        model = artifacts["model"]
        prediction = model.predict(X_pca)[0]
        probability = model.predict_proba(X_pca).max()
        
        is_fraud = bool(prediction)
        
        # Trigger n8n if fraud suspected
        if is_fraud or probability > FRAUD_THRESHOLD:
            logger.info(f"Fraude suspectée ({probability:.2f}). Déclenchement alerte.")
            background_tasks.add_task(trigger_fraud_alert, data, probability)
            
        return {
            "prediction": is_fraud,
            "probability": float(probability)
        }
        
    except Exception as e:
        logger.error(f"Erreur prédiction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def feedback(feedback_data: FeedbackInput, background_tasks: BackgroundTasks):
    try:
        logger.info("Feedback reçu.")
        # Re-calcul du PCA pour sauvegarde
        data = feedback_data.payload
        X_pca = process_features(data)
        
        # Sauvegarde
        pca_cols = [f'PCA_{i+1}' for i in range(X_pca.shape[1])]
        row_df = pd.DataFrame(X_pca, columns=pca_cols)
        row_df['target'] = feedback_data.correct_class
        row_df['prediction'] = feedback_data.prediction
        
        file_path = '/data/prod_data.csv'
        header = not os.path.exists(file_path)
        row_df.to_csv(file_path, mode='a', header=header, index=False)
        
        # Check Retrain
        background_tasks.add_task(check_and_retrain)
        
        return {"status": "recorded"}
        
    except Exception as e:
        logger.error(f"Erreur feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))
