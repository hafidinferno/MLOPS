from fastapi import FastAPI, HTTPException
from main import run_pipeline

app = FastAPI(
    title="Système de Recommandation Bancaire",
    description="API pour recommander des produits basés sur l'historique des transactions.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de Recommandation. Utilisez /recommend/{client_id}"}

@app.get("/recommend/{client_id}")
def get_recommendation(client_id: str):
    """
    Lance le pipeline de recommandation pour un client donné.
    """
    
    # Exécution du pipeline
    try:
        result = run_pipeline(client_id)
        if result is None:
             raise HTTPException(status_code=404, detail="Client introuvable ou pas d'historique")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
