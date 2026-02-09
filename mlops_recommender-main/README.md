# Système de Recommandation Bancaire IA (LSTM + FastAPI)

Ce projet est un système complet de recommandation de produits bancaires piloté par une Intelligence Artificielle (LSTM). Il analyse l'historique des transactions (`merchant_category`) pour prédire le prochain besoin du client et envoie automatiquement une offre par email.

##  Architecture

1.  **Données (`synthetic_fraud_data.csv`)** : Dataset réel contenant les transactions.
2.  **ETL (`processor.py`)** : Extrait les transactions d'un client et prépare une séquence de **80 items**.
3.  **IA (`model_service.py` / `train_model.py`)** :
    *   Un modèle **LSTM (TensorFlow/Keras)** entraîné sur les séquences d'achats.
    *   Prédit la prochaine catégorie de dépense probable.
    *   Mappe cette catégorie vers un produit bancaire (ex: "Gas" -> "Carte Essence Cashback").
4.  **API (`api.py`)** : Interface REST (FastAPI) pour interroger le système.
5.  **Action (`email_service.py`)** : Envoie un email réel (SMTP/Gmail) si la confiance est suffisante.

---

##  Installation

Assurez-vous d'avoir Python 3.10+ installé.

1.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```
    *(Inclut tensorflow, pandas, fastapi, uvicorn, scikit-learn)*

2.  **Configuration Email**
    Le fichier `email_service.py` est configuré pour envoyer des emails via Gmail.
    *   Expéditeur : Configuré (via Variables d'env ou par défaut).
    *   Destinataire : Hardcodé à `hafidyugi@gmail.com` (pour la démo).

---

##  Entraînement

Si vous n'avez pas encore les fichiers `lstm_model.h5` et `tokenizer.pickle`, vous devez entraîner le modèle :

```bash
python3 train_model.py
```
*Cela va lire les 50 000 premières lignes du CSV, entraîner le réseau de neurones et sauvegarder le "cerveau" de l'IA.*

---

##  Utilisation (API)

Le système s'utilise principalement via son API Web.

### 1. Démarrer le Serveur
```bash
uvicorn api:app --reload --port 8001
```

### 2. Obtenir une Recommandation
Ouvrez votre navigateur ou utilisez `curl` avec un ID client existant dans votre fichier CSV (ex: `CUST_72886`).

 **URL :** `http://127.0.0.1:8001/recommend/CUST_72886`

**Réponse JSON :**
```json
{
  "client_id": "CUST_72886",
  "recommended_product": "Carte Essence Cashback",
  "confidence": 0.82,
  "email_sent": true,
  "threshold": 0.0
}