import csv
import os

# Fichier de données réel
DATA_FILE = "synthetic_fraud_data.csv"

def get_client_transactions(client_id):
    """
    Récupère l'historique des transactions pour un client depuis le dataset réel.
    Retourne la liste des catégories marchandes ('merchant_category').
    """
    transactions = []
    
    if not os.path.exists(DATA_FILE):
        print(f"ERREUR: Le fichier {DATA_FILE} est introuvable.")
        return []

    try:
        with open(DATA_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Filtrage sur 'customer_id'
                if row["customer_id"] == client_id:
                    # On récupère la catégorie merchande
                    cat = row["merchant_category"]
                    transactions.append(cat)
                        
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        return []
        
    return transactions

def prepare_sequence(transactions, seq_length=80):
    """
    Prépare la séquence exact de 80 transactions (Focus 80).
    
    Logique:
    - Si historique > 80 : On coupe les anciennes (on garde les dernières).
    - Si historique < 80 : On complète avec des vides (padding) au début.
    """
    data = list(transactions)
    current_len = len(data)
    
    if current_len == seq_length:
        return data
        
    if current_len > seq_length:
        # On garde les 'seq_length' derniers éléments
        return data[-seq_length:]
        
    if current_len < seq_length:
        # Padding au début avec des 0 (ou une valeur vide)
        padding_needed = seq_length - current_len
        # Supposons que '0' représente une transaction vide/nulle
        padding = [0] * padding_needed 
        return padding + data

# Test rapide si exécuté directement
if __name__ == "__main__":
    t1 = prepare_sequence(range(100))
    print(f"Len t1 (org 100): {len(t1)}, Starts with: {t1[0]}")
    
    t2 = prepare_sequence(range(50))
    print(f"Len t2 (org 50): {len(t2)}, Starts with: {t2[0]}")
