# 🛡️ SecurePay - MLOps Fraud Detection

Project MLOps complet incluant Entraînement, API Serving, Interface Web et Monitoring.

## 🚀 Quick Start

1. **Entraînement** (Génération des artefacts) :
   ```bash
   python scripts/train_model.py --nrows 100000
   ```

2. **Lancement** (Docker) :
   ```bash
   docker-compose up --build -d
   ```

## 🔗 Accès aux Services

| Service | URL | Description |
|---|---|---|
| **Web App** 🖥️ | [http://localhost:8501](http://localhost:8501) | Interface de détection de fraude (Streamlit) |
| **Serving API** ⚙️ | [http://localhost:8080/docs](http://localhost:8080/docs) | API d'inférence (FastAPI / Swagger) |
| **Reporting** 📊 | [http://localhost:8000](http://localhost:8000) | Dashboard de Monitoring (Evidently) |
| **Automation** 🤖 | [http://localhost:5679](http://localhost:5679) | Workflow et Alerting (n8n) |

## 🛠️ Dépannage
Si `localhost` ne fonctionne pas (WSL), essayez l'IP locale :
`wsl hostname -I`
puis, par exemple : `http://172.x.x.x:8501`.
