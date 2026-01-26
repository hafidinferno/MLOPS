import pandas as pd
import numpy as np
import pickle
import os
import argparse
import logging
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score, accuracy_score, classification_report
import xgboost as xgb

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train_and_save(data_path, output_dir, artifacts_dir, nrows=None, n_estimators=50, max_depth=10):
    logger.info(f"Démarrage de l'entraînement. Data: {data_path}, Max Rows: {nrows}")
    
    try:
        # Load Data
        df = pd.read_csv(data_path, nrows=nrows)
        logger.info(f"Données chargées: {df.shape}")
    except FileNotFoundError:
        logger.error(f"Fichier non trouvé: {data_path}")
        return
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données: {e}")
        return

    # Preprocessing
    logger.info("Début du preprocessing...")
    
    # Drop columns
    drop_cols = [
        'transaction_id', 'customer_id', 'card_number', 'timestamp', 
        'merchant', 'city', 'device_fingerprint', 'ip_address', 
        'velocity_last_hour'
    ]
    df = df.drop(columns=drop_cols, errors='ignore')
    
    # Features & Target
    # Features & Target
    is_preprocessed = False
    if 'target' in df.columns and 'PCA_1' in df.columns:
        logger.info("Données déjà traitées (PCA) détectées.")
        is_preprocessed = True
        X = df.drop(columns=['target'])
        y = df['target']
    elif 'is_fraud' in df.columns:
        X = df.drop(columns=['is_fraud'])
        y = df['is_fraud']
    else:
        logger.error("Colonne cible manquante ('is_fraud' ou 'target').")
        return
    
    # Validation du split (Optionnel mais recommandé pour évaluer)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Preprocessing et PCA seulement si données brutes
    if is_preprocessed:
        logger.info("Données déjà PCA, skip preprocessing.")
        X_train_pca = X_train_raw
        X_test_pca = X_test_raw
    else:
        # Identification des colonnes
        categorical_cols = X.select_dtypes(include=['object', 'bool']).columns.tolist()
        numerical_cols = X.select_dtypes(include=['number']).columns.tolist()
        
        logger.info(f"Colonnes numériques: {len(numerical_cols)}")
        logger.info(f"Colonnes catégorielles: {len(categorical_cols)}")

        # Pipeline de transformation
        numeric_transformer = StandardScaler()
        categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)

        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numerical_cols),
                ('cat', categorical_transformer, categorical_cols)
            ]
        )

        # Fit Transform sur X_train, Transform sur X_test
        logger.info("Application du Preprocessor...")
        X_train_processed = preprocessor.fit_transform(X_train_raw)
        X_test_processed = preprocessor.transform(X_test_raw)
        
        # PCA
        n_components = 10
        pca = PCA(n_components=n_components)
        logger.info(f"Application PCA ({n_components} composants)...")
        X_train_pca = pca.fit_transform(X_train_processed)
        X_test_pca = pca.transform(X_test_processed)
        
        # Sauvegarde des artefacts de preprocessing
        logger.info("Sauvegarde des artefacts de preprocessing...")
        with open(os.path.join(artifacts_dir, 'preprocessor.pickle'), 'wb') as f:
            pickle.dump(preprocessor, f)
            
        with open(os.path.join(artifacts_dir, 'pca.pickle'), 'wb') as f:
            pickle.dump(pca, f)

    # Entraînement Modèle Random Forest
    logger.info("Entraînement du modèle RandomForest...")
    rf_clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    rf_clf.fit(X_train_pca, y_train)

    # Évaluation RF
    y_pred_rf = rf_clf.predict(X_test_pca)
    f1_rf = f1_score(y_test, y_pred_rf)
    acc_rf = accuracy_score(y_test, y_pred_rf)
    
    logger.info(f"RandomForest - F1-Score: {f1_rf:.4f}, Accuracy: {acc_rf:.4f}")
    logger.info("\n" + classification_report(y_test, y_pred_rf))

    # Entraînement Modèle XGBoost
    logger.info("Entraînement du modèle XGBoost...")
    xgb_clf = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    xgb_clf.fit(X_train_pca, y_train)

    # Évaluation XGBoost
    y_pred_xgb = xgb_clf.predict(X_test_pca)
    f1_xgb = f1_score(y_test, y_pred_xgb)
    acc_xgb = accuracy_score(y_test, y_pred_xgb)

    logger.info(f"XGBoost - F1-Score: {f1_xgb:.4f}, Accuracy: {acc_xgb:.4f}")
    logger.info("\n" + classification_report(y_test, y_pred_xgb))

    # Comparaison et Sélection du meilleur modèle
    if f1_xgb > f1_rf:
        best_model = xgb_clf
        best_model_name = "XGBoost"
        logger.info(f"Le meilleur modèle est XGBoost avec un F1-Score de {f1_xgb:.4f}")
    else:
        best_model = rf_clf
        best_model_name = "RandomForest"
        logger.info(f"Le meilleur modèle est RandomForest avec un F1-Score de {f1_rf:.4f}")

    # Sauvegarde des données de référence (Training data transformé) pour Drift Monitoring
    # Si on a déjà utilisé ref_data comme entrée, on ne l'écrase pas nécessairement, ou on le laisse tel quel.
    if not is_preprocessed:
        logger.info("Sauvegarde des données de référence...")
        os.makedirs(output_dir, exist_ok=True)
        
        # On suppose n_components défini dans le bloc else plus haut
        pca_cols = [f'PCA_{i+1}' for i in range(10)] # Hardcoded or passed variable
        ref_df = pd.DataFrame(X_train_pca, columns=pca_cols)
        ref_df['target'] = y_train.values
        
        ref_file = os.path.join(output_dir, 'ref_data.csv')
        ref_df.to_csv(ref_file, index=False)
        logger.info(f"Données de référence sauvegardées dans {ref_file}")
    else:
        logger.info("Données d'entrée déjà transformées (ref_data). Pas de nouvelle sauvegarde de ref_data.")

    # Sauvegarde des artefacts
    logger.info("Sauvegarde des artefacts...")
    os.makedirs(artifacts_dir, exist_ok=True)

        
    # Artefacts preprocessing sauvegardés plus haut seulement si créés
        
    with open(os.path.join(artifacts_dir, 'model.pickle'), 'wb') as f:
        pickle.dump(best_model, f)
    
    with open(os.path.join(artifacts_dir, 'model_metadata.txt'), 'w') as f:
        f.write(f"Best Model: {best_model_name}")
    
    logger.info("Terminé.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script d'entraînement MLOps")
    parser.add_argument("--data_path", type=str, default="data/ref_data.csv", help="Chemin vers le CSV de données")
    parser.add_argument("--output_dir", type=str, default="data", help="Dossier pour les données générées (ref_data)")
    parser.add_argument("--artifacts_dir", type=str, default="artifacts", help="Dossier pour les modèles sauvegardés")
    parser.add_argument("--nrows", type=int, default=100000, help="Nombre de lignes à lire (None pour tout)")
    parser.add_argument("--n_estimators", type=int, default=50, help="RandomForest n_estimators")
    parser.add_argument("--max_depth", type=int, default=10, help="RandomForest max_depth")

    args = parser.parse_args()
    
    train_and_save(
        data_path=args.data_path, 
        output_dir=args.output_dir, 
        artifacts_dir=args.artifacts_dir,
        nrows=args.nrows,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth
    )
