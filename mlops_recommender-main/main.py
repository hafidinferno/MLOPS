from processor import get_client_transactions, prepare_sequence
from model_service import LSTMRecommender
from email_service import send_recommendation_email

CONFIDENCE_THRESHOLD = 0.0

def run_pipeline(client_id):
    print(f"--- Démarrage du pipeline pour {client_id} ---")
    
    # 1. Extraction
    raw_history = get_client_transactions(client_id)
    if not raw_history:
        print(f"Aucun historique trouvé pour {client_id}. Fin du processus.")
        return

    print(f"1. Historique brut récupéré : {len(raw_history)} transactions")

    # 2. Fenêtrage (Focus 80)
    sequence_80 = prepare_sequence(raw_history)
    print(f"2. Séquence préparée (taille {len(sequence_80)}) : {sequence_80[:5]}... (début)")

    # 3. Prédiction LSTM
    recommender = LSTMRecommender()
    product, probability = recommender.predict(sequence_80)
    print(f"3. Prédiction LSTM : Produit='{product}', Confiance={probability:.4f}")

    # 4. Décision & Action
    email_sent = False
    if probability > CONFIDENCE_THRESHOLD:
        print(f"4. Décision : Score {probability:.4f} > {CONFIDENCE_THRESHOLD}. Envoi de l'email.")
        send_recommendation_email(client_id, product, probability)
        email_sent = True
    else:
        print(f"4. Décision : Score {probability:.4f} <= {CONFIDENCE_THRESHOLD}. Pas d'email envoyé.")
    
    print("-" * 30 + "\n")
    
    return {
        "client_id": client_id,
        "recommended_product": product,
        "confidence": probability,
        "email_sent": email_sent,
        "threshold": CONFIDENCE_THRESHOLD
    }

if __name__ == "__main__":
    # Test avec un ID qui existe probablement dans votre fichier
    # Remplacez 'C1093826151' par un vrai ID de votre dataset synthetic_fraud_data.csv
    print("Pour tester, lancez l'API ou utilisez un ID présent dans votre CSV.")
    # run_pipeline("C1093826151") 

