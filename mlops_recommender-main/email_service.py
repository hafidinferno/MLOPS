import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# CONFIGURATION SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
# Expéditeur (Votre compte pour envoyer)
SENDER_EMAIL = os.getenv("SMTP_EMAIL", "talaharichihab3519@gmail.com")
SENDER_PASSWORD = os.getenv("SMTP_PASSWORD", "mbrd kxza nqfy cxgo")

# DESTINATAIRE UNIQUE (Toujours envoyer ici)
RECIPIENT_EMAIL = "hafidyugi@gmail.com"

# TEMPLATE HTML
EMAIL_TEMPLATE = """
<html>
  <body>
    <h2>Nouvelle Recommandation Bancaire</h2>
    <p>Bonjour,</p>
    <p>Suite à l'analyse des transactions du client <b>{client_id}</b>, nous avons une recommandation :</p>
    <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; border: 1px solid #00aabb;">
      <h3 style="color: #0056b3; margin-top: 0;">Produit : {product_name}</h3>
    </div>
    <p>Cordialement,<br>L'équipe de la banque</p>
  </body>
</html>
"""

def send_recommendation_email(client_id, product_name, probability):
    """
    Envoie un email via SMTP au destinataire unique.
    """
    print(f"[@EMAIL SERVICE] Tentative d'envoi d'email à {RECIPIENT_EMAIL}...")
    
    # Vérification basique des credentials
    if "votre_email" in SENDER_EMAIL or "votre_mot_de_passe" in SENDER_PASSWORD:
        print("[@EMAIL SERVICE]  ERREUR: Credentials SMTP non configurés.")
        print("   -> Veuillez définir les variables d'environnement SMTP_EMAIL et SMTP_PASSWORD.")
        print("   -> Ou modifiez directement le fichier email_service.py.")
        return

    try:
        # Création du message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = f"Recommandation pour {client_id} : {product_name}"

        # Corps du message
        body = EMAIL_TEMPLATE.format(
            client_id=client_id,
            product_name=product_name,
            probability=probability
        )
        msg.attach(MIMEText(body, 'html'))

        # Connexion au serveur SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Sécurisation de la connexion
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Envoi
        server.send_message(msg)
        server.quit()
        
        print(f"[@EMAIL SERVICE] Email envoyé avec succès à {RECIPIENT_EMAIL} !")
        
    except Exception as e:
        print(f"[@EMAIL SERVICE] Erreur lors de l'envoi de l'email : {e}")
