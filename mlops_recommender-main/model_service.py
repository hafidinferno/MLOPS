import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import os

MODEL_FILE = "lstm_model.h5"
TOKENIZER_FILE = "tokenizer.pickle"
SEQ_LENGTH = 80

class LSTMRecommender:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.cat_to_int = None
        self.int_to_cat = None
        
        # Chargement du modèle
        if os.path.exists(MODEL_FILE):
            print(f"Chargement du modèle {MODEL_FILE}...")
            # On charge le modèle (attention format h5 legacy)
            self.model = load_model(MODEL_FILE)
        else:
            print("Modele introuvable. Veuillez lancer train_model.py")
            
        # Chargement du tokenizer
        if os.path.exists(TOKENIZER_FILE):
            with open(TOKENIZER_FILE, 'rb') as handle:
                data = pickle.load(handle)
                self.cat_to_int = data['cat_to_int']
                self.int_to_cat = data['int_to_cat']
                
    def predict(self, sequence):
        """
        Analyse la séquence de 80 items (noms de catégories) et prédit la prochaine.
        """
        if self.model is None or self.tokenizer is None:
             # Fallback si pas de modèle (pour éviter le crash)
             # Mais normalement on devrait avoir le modèle
             if self.model is None: return "Modele Non Chargé", 0.0
             
        # sequence est une liste de strings ex: ['Gas', 'Food'...]
        # On doit convertir en int
        encoded_seq = []
        if self.cat_to_int:
            for cat in sequence:
                # Si la catégorie est inconnue (0 ou nouvelle), on met 0 (padding)
                encoded_seq.append(self.cat_to_int.get(cat, 0))
        else:
            return "Erreur Tokenizer", 0.0

        # On pad si nécessaire (bien que l'entrée soit supposée être 80)
        padded_seq = pad_sequences([encoded_seq], maxlen=SEQ_LENGTH, padding='pre')
        
        # Prédiction
        prediction = self.model.predict(padded_seq, verbose=0)
        # prediction est un tableau de probabilités [0.1, 0.05, 0.8, ...]
        
        # Trouver l'index avec la plus haute proba
        predicted_index = np.argmax(prediction[0])
        probability = float(prediction[0][predicted_index])
        
        # Retrouver le nom de la catégorie
        predicted_category = self.int_to_cat.get(predicted_index, "Inconnu")
        
        # Mapping Catégorie -> Produit Bancaire (Règle métier)
        product_map = {
            "Gas": "Carte Essence Cashback",
            "Entertainment": "Assurance Loisirs",
            "Grocery": "Compte Budget Famille",
            "Travel": "Assurance Voyage Gold",
            "Shopping": "Carte Premium",
            "Online": "Assurance Achats Web",
            "Restaurant": "Carte Restaurant",
            "Transport": "Pass Mobilité",
            "Utilities": "Service Paiement Factures"
        }
        
        # Si la catégorie n'est pas dans la map, on propose un produit par défaut
        recommended_product = product_map.get(predicted_category, f"Offre Spéciale ({predicted_category})")
        
        return recommended_product, probability
