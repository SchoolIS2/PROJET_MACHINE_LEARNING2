import os
import sys
import django
from dotenv import load_dotenv

# 1. Charger les variables d'environnement du fichier .env
load_dotenv()

def init_django():
    """Initialise le contexte Django pour permettre aux scripts externes
    (comme tes futurs scrapers ou scripts de Deep Learning) d'interagir
    avec la base de données et les modèles de l'application."""
    
    # Indique à Django où se trouvent ses paramètres (dans core/settings.py)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    try:
        django.setup()
        print("[INFO] Environnement Django initialisé avec succès pour les scripts externes.")
    except Exception as e:
        print(f"[ERREUR] Impossible d'initialiser Django : {e}")
        sys.exit(1)

def main():
    print("=== Lancement du script autonome (ProjetML2) ===")
    
    # Initialisation
    init_django()
    
    # ------------------------------------------------------------------------
    # TODO : C'est ici que tu placeras tes fonctions de test.
    # Exemples :
    # 1. Lancer un scraper : extraire_donnees_web()
    # 2. Entraîner ton modèle : entrainer_modele_deep(donnees_scrapees)
    # 3. Sauvegarder les prédictions directement dans tes tables Django
    # ------------------------------------------------------------------------
    
    print("[SUCCESS] Fin de l'exécution du script principal.")

if __name__ == "__main__":
    main()
