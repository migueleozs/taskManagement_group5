# taskmanagement
pour la contenerisation de backend et frontend on a créer:
 un fichier dockerfile dans le backend 
 un fichier dockerfile dans le frontend
puis un fichier docker-compose.yml dans la racine du projet

par apres on a lancer les commandes suivantes : 
# 1. Build et démarrage (première fois)
docker-compose up --build

# 2. Démarrer en arrière-plan (détaché)
docker-compose up -d
# 3. Voir les logs
docker-compose logs -f

# 4. Arrêter les conteneurs
docker-compose down


