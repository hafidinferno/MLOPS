# 🛡️ SecurePay - MLOps Fraud Detection

Project MLOps complet incluant Entraînement (XGBoost/RandomForest), API Serving, Interface Web Professionnelle et Monitoring.

## 🚀 Quick Start

### 1. Entraînement (Génération des artefacts)

Le script va entraîner les modèles, sélectionner le meilleur (XGBoost ou RF) et sauvegarder les artefacts.

```bash
python scripts/train_model.py
```

_Note: Les données utilisées seront `data/ref_data.csv` (Données PCA pré-traitées)._

### 2. Lancement (Docker)

Pour lancer tous les services (API, Webapp, Reporting, n8n) :

**Premier lancement ou après modification du code :**

```bash
docker-compose up --build -d
```

**Si vous avez des erreurs de ports ou de conflits :**

```bash
# Arrêter et supprimer les conteneurs existants
docker-compose down

# (Optionnel) Forcer la suppression si bloqué
docker rm -f serving-api webapp reporting n8n

# Relancer
docker-compose up --build -d
```

## 🔗 Accès aux Services

| Service            | URL                                                      | Description                                          |
| ------------------ | -------------------------------------------------------- | ---------------------------------------------------- |
| **Web App** 🖥️     | [http://localhost:8501](http://localhost:8501)           | Interface de détection de fraude (Streamlit Premium) |
| **Serving API** ⚙️ | [http://localhost:8080/docs](http://localhost:8080/docs) | API d'inférence (FastAPI / Swagger)                  |
| **Reporting** 📊   | [http://localhost:8000](http://localhost:8000)           | Dashboard de Monitoring (Evidently)                  |
| **Automation** 🤖  | [http://localhost:5678](http://localhost:5678)           | Workflow et Alerting (n8n)                           |

## ✨ Nouvelles Fonctionnalités

- **Modele Hybride**: Comparaison automatique entre Random Forest et **XGBoost**.
- **Frontend Premium**: Nouvelle interface "Glassmorphism" avec analyses visuelles (Radar Charts).
- **Architecture**: Utilisation de données de référence pré-calculées pour un entraînement plus rapide.

## 🛠️ Dépannage

Si `localhost` ne fonctionne pas (WSL), essayez l'IP locale :
`wsl hostname -I`
puis, par exemple : `http://172.x.x.x:8501`.

Si vous avez l'erreur `Bind for 0.0.0.0:8080 failed`, cela signifie que le port 8080 est déjà utilisé.
Assurez-vous qu'aucun autre service n'utilise ce port, ou modifiez le mapping de port dans `docker-compose.yml`.
