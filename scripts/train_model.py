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
    if 'is_fraud' not in df.columns:
        logger.error("Colonne cible 'is_fraud' manquante.")
        return

    X = df.drop(columns=['is_fraud'])
    y = df['is_fraud']
    
    # Validation du split (Optionnel mais recommandé pour évaluer)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

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

    # Entraînement Modèle
    logger.info("Entraînement du modèle RandomForest...")
    clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
    clf.fit(X_train_pca, y_train)

    # Évaluation
    y_pred = clf.predict(X_test_pca)
    f1 = f1_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)
    
    logger.info(f"Modèle entraîné. F1-Score: {f1:.4f}, Accuracy: {acc:.4f}")
    logger.info("\n" + classification_report(y_test, y_pred))

    # Sauvegarde des données de référence (Training data transformé) pour Drfit Monitoring
    # On sauvegarde une partie pour pas faire exploser le fichier
    logger.info("Sauvegarde des données de référence...")
    os.makedirs(output_dir, exist_ok=True)
    
    pca_cols = [f'PCA_{i+1}' for i in range(n_components)]
    ref_df = pd.DataFrame(X_train_pca, columns=pca_cols)
    ref_df['target'] = y_train.values
    
    ref_file = os.path.join(output_dir, 'ref_data.csv')
    ref_df.to_csv(ref_file, index=False)
    logger.info(f"Données de référence sauvegardées dans {ref_file}")

    # Sauvegarde des artefacts
    logger.info("Sauvegarde des artefacts...")
    os.makedirs(artifacts_dir, exist_ok=True)

    with open(os.path.join(artifacts_dir, 'preprocessor.pickle'), 'wb') as f:
        pickle.dump(preprocessor, f)
        
    with open(os.path.join(artifacts_dir, 'pca.pickle'), 'wb') as f:
        pickle.dump(pca, f)
        
    with open(os.path.join(artifacts_dir, 'model.pickle'), 'wb') as f:
        pickle.dump(clf, f)
    
    logger.info("Terminé.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script d'entraînement MLOps")
    parser.add_argument("--data_path", type=str, default="synthetic_fraud_data.csv", help="Chemin vers le CSV de données")
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
