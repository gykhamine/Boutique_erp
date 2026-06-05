# 🏪 Boutique ERP — Système de gestion complet

Système ERP style Odoo développé avec Django, conçu pour les boutiques en Afrique francophone (FCFA, hors-ligne, SQLite).

---

## ✅ Les 15 fonctionnalités principales

| # | Module | Description |
|---|--------|-------------|
| 1 | **Tableau de bord** | KPIs temps réel, graphiques ventes 7j, alertes stock |
| 2 | **Gestion produits** | Catalogue complet avec QR codes auto-générés (qrcode) |
| 3 | **Ventes** | Création ventes multi-lignes, calcul TVA/remise automatique |
| 4 | **Achats** | Commandes fournisseurs, réception → mise à jour stock auto |
| 5 | **Gestion clients** | Fiches clients, historique achats, gestion crédit |
| 6 | **Gestion fournisseurs** | Annuaire fournisseurs, délais livraison |
| 7 | **Stock** | Mouvements stock, ajustements, inventaire complet |
| 8 | **Caisse** | Sessions caisse, transactions entrées/sorties, clôture |
| 9 | **Facturation PDF** | Génération PDF professionnels (ReportLab + PyPDF2) |
| 10 | **Rapports** | Graphiques matplotlib, analyse pandas, export Excel openpyxl |
| 11 | **Ressources humaines** | Fiches employés, gestion congés |
| 12 | **Tâches Kanban** | Board To-do / En cours / Terminé avec priorités |
| 13 | **Notifications** | Alertes automatiques stock faible, système de notifications |
| 14 | **Tâches asynchrones** | Celery + Redis : rapports auto, vérifications planifiées |
| 15 | **Paramètres** | Configuration boutique, gestion utilisateurs |

---

## 📦 Modules Python utilisés

| Module | Usage dans le projet |
|--------|----------------------|
| `qrcode` | Génération QR code pour chaque produit (référence, prix, nom) |
| `matplotlib` | Graphiques ventes journalières et camembert catégories |
| `pandas` | Analyse statistique avancée des ventes (moyenne, CA mensuel) |
| `PyPDF2` | Lecture métadonnées PDF, fusion de documents |
| `openpyxl` | Export Excel multi-feuilles avec graphiques et mise en forme |
| `sqlite3` | Base de données principale (Django SQLite backend) |
| `celery` | Tâches asynchrones : alertes stock, rapports journaliers |

---

## 🚀 Installation rapide

### 1. Prérequis
- Python 3.10+
- pip
- (Optionnel) Redis pour Celery

### 2. Installation automatique
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Installation manuelle
```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# Installer les dépendances
pip install -r requirements.txt

# Base de données
python manage.py makemigrations
python manage.py migrate

# Compte admin
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

### 4. Accès
- **URL**: http://127.0.0.1:8000
- **Admin Django**: http://127.0.0.1:8000/admin
- **Login demo**: `admin` / `admin123` (après setup.sh)

---

## ⚙️ Celery (tâches automatiques)

Redis requis (facultatif, pour les alertes automatiques) :

```bash
# Installer Redis sur Ubuntu
sudo apt install redis-server
sudo systemctl start redis

# Lancer le worker Celery
celery -A boutique_erp worker -l info

# Lancer le scheduler (tâches périodiques)
celery -A boutique_erp beat -l info
```

**Tâches automatiques disponibles :**
- `verifier_stocks_faibles()` — Détecte et notifie les ruptures
- `rapport_journalier()` — Résumé des ventes du jour

---

## 📁 Structure du projet

```
boutique_erp/
├── boutique_erp/          # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── celery.py          # Config Celery
├── apps/
│   ├── dashboard/         # Tableau de bord
│   ├── produits/          # Catalogue + QR codes
│   ├── ventes/            # Point de vente
│   ├── achats/            # Commandes fournisseurs
│   ├── clients/           # CRM clients
│   ├── fournisseurs/      # Annuaire fournisseurs
│   ├── stock/             # Gestion inventaire
│   ├── caisse/            # Caisse enregistreuse
│   ├── factures/          # Facturation PDF
│   ├── rapports/          # Analyses & exports
│   ├── employes/          # RH
│   ├── taches/            # Kanban
│   ├── notifications/     # Alertes système
│   └── parametres/        # Configuration
├── templates/             # Templates HTML Bootstrap 5
├── static/                # CSS, JS, images
├── media/                 # Uploads (images, PDFs, QR codes)
├── requirements.txt
├── setup.sh               # Script d'installation
└── manage.py
```

---

## 🗄️ Base de données

SQLite par défaut (`boutique.sqlite3`). Pour PostgreSQL :

```python
# Dans settings.py, remplacer DATABASES par :
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'boutique_erp',
        'USER': 'postgres',
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 🌍 Contexte africain

- Devise **FCFA** dans tous les formulaires et rapports
- Fuseau horaire **Africa/Brazzaville**
- Langue **Français**
- Fonctionne **100% hors-ligne** (SQLite, pas de cloud)
- Compatible déploiement sur **USB / Capsule Gykhamine**

---

## 📸 Modules & écrans

- Dashboard avec mini-graphique animé JS
- Liste produits avec QR codes, alertes rupture colorées
- Formulaire vente avec calcul automatique en temps réel
- Tableau Kanban drag-and-drop des tâches
- Rapport Excel 4 feuilles avec graphique openpyxl
- Factures PDF générées automatiquement via ReportLab

---
