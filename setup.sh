#!/bin/bash
# ============================================================
# BOUTIQUE ERP — Script d'installation automatique
# Compatible: Ubuntu/Debian, Rocky Linux, Fedora
# ============================================================

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         BOUTIQUE ERP — Installation                  ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trouvé. Installez Python 3.10+ d'abord."
    exit 1
fi

# Créer environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Migrations
echo "🗄️  Création de la base de données SQLite..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Superutilisateur
echo ""
echo "👤 Création du compte administrateur..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@boutique.cg', 'admin123')
    print('✅ Admin créé: admin / admin123')
else:
    print('ℹ️  Admin existe déjà')
"

# Données de démonstration
echo "🌱 Chargement des données de démonstration..."
python manage.py shell -c "
from apps.produits.models import Categorie, Produit
from apps.clients.models import Client
from apps.fournisseurs.models import Fournisseur

# Catégories
cats = ['Alimentaire', 'Boissons', 'Hygiène & Beauté', 'Électronique', 'Vêtements', 'Pharmacie', 'Papeterie', 'Quincaillerie']
cat_objs = {}
for c in cats:
    obj, _ = Categorie.objects.get_or_create(nom=c)
    cat_objs[c] = obj

# Produits de démonstration
produits = [
    {'ref': 'SAC001', 'nom': 'Sac de riz 25kg', 'cat': 'Alimentaire', 'achat': 18000, 'vente': 22000, 'stock': 50},
    {'ref': 'HUI001', 'nom': 'Huile palme 5L', 'cat': 'Alimentaire', 'achat': 5500, 'vente': 7000, 'stock': 30},
    {'ref': 'SUC001', 'nom': 'Sucre 1kg', 'cat': 'Alimentaire', 'achat': 800, 'vente': 1000, 'stock': 80},
    {'ref': 'CAF001', 'nom': 'Café Nescafé 200g', 'cat': 'Boissons', 'achat': 3500, 'vente': 4500, 'stock': 25},
    {'ref': 'EAU001', 'nom': 'Eau minérale 1.5L', 'cat': 'Boissons', 'achat': 400, 'vente': 600, 'stock': 120},
    {'ref': 'SAV001', 'nom': 'Savon Palmolive', 'cat': 'Hygiène & Beauté', 'achat': 400, 'vente': 600, 'stock': 60},
    {'ref': 'DEN001', 'nom': 'Dentifrice Signal 75ml', 'cat': 'Hygiène & Beauté', 'achat': 700, 'vente': 1000, 'stock': 40},
    {'ref': 'PHO001', 'nom': 'Chargeur téléphone USB-C', 'cat': 'Électronique', 'achat': 3000, 'vente': 5000, 'stock': 15},
    {'ref': 'CAH001', 'nom': 'Cahier 200 pages', 'cat': 'Papeterie', 'achat': 500, 'vente': 700, 'stock': 5, 'min': 10},
    {'ref': 'STY001', 'nom': 'Stylo bille Bic (lot 10)', 'cat': 'Papeterie', 'achat': 1000, 'vente': 1500, 'stock': 20},
]
for p in produits:
    if not Produit.objects.filter(reference=p['ref']).exists():
        Produit.objects.create(
            reference=p['ref'], nom=p['nom'],
            categorie=cat_objs[p['cat']],
            prix_achat=p['achat'], prix_vente=p['vente'],
            stock_actuel=p['stock'], stock_minimum=p.get('min', 5)
        )

# Clients
clients = [
    {'nom': 'Marie Mbemba', 'tel': '06-123-4567', 'ville': 'Brazzaville', 'type': 'particulier'},
    {'nom': 'Jean-Pierre Makoundi', 'tel': '06-234-5678', 'ville': 'Brazzaville', 'type': 'particulier'},
    {'nom': 'Épicerie du Marché', 'tel': '05-345-6789', 'ville': 'Pointe-Noire', 'type': 'entreprise'},
    {'nom': 'Supermarché Kin', 'tel': '05-456-7890', 'ville': 'Brazzaville', 'type': 'entreprise'},
]
for c in clients:
    if not Client.objects.filter(nom=c['nom']).exists():
        Client.objects.create(nom=c['nom'], telephone=c['tel'], ville=c['ville'], type_client=c['type'])

# Fournisseurs
fournisseurs = [
    {'nom': 'SOCAS Distribution', 'contact': 'M. Kouba', 'tel': '05-111-2222'},
    {'nom': 'Congo Import-Export', 'contact': 'Mme Bongo', 'tel': '06-333-4444'},
]
for f in fournisseurs:
    if not Fournisseur.objects.filter(nom=f['nom']).exists():
        Fournisseur.objects.create(nom=f['nom'], contact=f['contact'], telephone=f['tel'])

print('✅ Données de démo chargées.')
"

# Fichiers statiques
echo "🎨 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput -v 0

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  ✅ INSTALLATION TERMINÉE                            ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  Lancer: python manage.py runserver                  ║"
echo "║  URL: http://127.0.0.1:8000                          ║"
echo "║  Admin: admin / admin123                             ║"
echo "║                                                      ║"
echo "║  Pour Celery (optionnel, nécessite Redis):           ║"
echo "║  celery -A boutique_erp worker -l info               ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
