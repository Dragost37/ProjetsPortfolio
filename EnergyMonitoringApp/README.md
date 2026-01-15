# Tableau de Bord Énergétique - Énergie Réunion

Application de suivi et visualisation de la consommation énergétique par source d'énergie pour l'île de la Réunion.

## Vue d'ensemble

Cette application permet de :
- ✅ Enregistrer des mesures de consommation énergétique
- ✅ Organiser les données par catégories (6 sources) et sous-catégories
- ✅ Visualiser les données sur un **dashboard interactif** avec stacked bar chart
- ✅ Consulter l'historique complet avec filtres
- ✅ Voir le détail des sous-catégories au survol du graphique

### Sources d'énergie supportées
- **Solaire** (Photovoltaïque, Solaire thermique)
- **Éolien** (Éolien terrestre, Éolien offshore)
- **Hydraulique** (Au fil de l'eau, De lac, À remontée)
- **Biomasse** (Bagasse, Bois, Biogaz, Bioéthanol, Bioliquide)
- **Autres EnR** (Géothermie, ETM, Houlomotrice, ORC)
- **Récupération** (Huiles usagées, CSR, Chaleur fatale, Récupération thermique)

---

## Tech Stack

| Composant | Technologie |
|-----------|------------|
| **Backend** | FastAPI (Python 3.10+) |
| **Frontend** | Jinja2 Templates + Vanilla JavaScript |
| **Visualisation** | D3.js v7 |
| **Base de données** | PostgreSQL 15 |
| **ORM** | SQLAlchemy |
| **Conteneurisation** | Docker + Docker Compose |
| **Accessibilité** | WCAG 2.1 AAA Compliant |

---

## Prérequis

- **Docker** 20.10+
- **Docker Compose** 2.0+
- (Optionnel) **Python** 3.10+ pour développement local

---

## Démarrage rapide

### 1. Cloner le projet
```bash
git clone https://github.com/Dragost37/ProjetsPortfolio.git
cd EnergyMonitoringApp
```

### 2. Lancer l'application
```bash
docker compose up --build
```

### 3. Accéder à l'application
- **Interface Web** : http://localhost:8000
- **API Swagger** : http://localhost:8000/docs
- **API ReDoc** : http://localhost:8000/redoc

### 4. Arrêter l'application
```bash
docker compose down
```

---

## Structure du projet

```
EnergyMonitoringApp/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── models.py            # Modèles SQLAlchemy
│   ├── schemas.py           # Schémas de validation
│   ├── crud.py              # Opérations CRUD
│   ├── database.py          # Configuration DB
│   ├── static/
│   │   ├── app.js           # Scripts frontend
│   │   └── styles.css       # Feuille de styles
│   └── templates/
│       ├── base.html        # Layout principal
│       ├── dashboard.html   # Page dashboard
│       ├── form.html        # Formulaire d'enregistrement
│       └── list.html        # Page liste
├── docker-compose.yml       # Configuration Docker
├── Dockerfile               # Image Docker
├── requirements.txt         # Dépendances Python
└── README.md               # Ce fichier
```

---

## Modèle de données

### Relations
```
Category (1) ──── (N) SubCategory ──── (N) EnergyRecord
```

### Tables principales

#### `categories`
```sql
CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  description TEXT
);
```

#### `subcategories`
```sql
CREATE TABLE subcategories (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
);
```

#### `energy_records`
```sql
CREATE TABLE energy_records (
  id SERIAL PRIMARY KEY,
  year INTEGER NOT NULL,
  value_kwh DECIMAL(12, 2) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  category_id INTEGER REFERENCES categories(id),
  subcategory_id INTEGER REFERENCES subcategories(id)
);
```

---

## Pages principales

### 1. **Dashboard** (`/dashboard`)
- Visualisation stacked bar chart (3 années)
- KPI cards (Total, Moyenne, Nombre d'enregistrements)
- **Focus + Context**: Survol d'une barre affiche le détail des sous-catégories
- Responsive et optimisé pour desktop/tablet

### 2. **Enregistrement** (`/form`)
- Formulaire pour ajouter/modifier une mesure
- Sélection dynamique des sous-catégories
- Modal pour créer une nouvelle catégorie
- Validation côté client et serveur

### 3. **Liste** (`/list`)
- Tableau de tous les enregistrements
- Filtrage par catégorie/sous-catégorie
- Suppression d'enregistrements
- Tags visuels pour catégories

---

## API Endpoints

### Catégories
```
GET    /api/categories                    # Lister toutes les catégories
POST   /api/categories                    # Créer une catégorie
GET    /api/categories/{id}               # Détail d'une catégorie
DELETE /api/categories/{id}               # Supprimer une catégorie
```

### Sous-catégories
```
GET    /api/subcategories                 # Lister (filtrable par category_id)
POST   /api/subcategories                 # Ajouter à une catégorie existante
DELETE /api/subcategories/{id}            # Supprimer une sous-catégorie
```

### Enregistrements énergétiques
```
GET    /api/energy-records                # Lister avec filtres
POST   /api/energy-records                # Créer un enregistrement
GET    /api/energy-records/{id}           # Détail d'un enregistrement
PUT    /api/energy-records/{id}           # Mettre à jour
DELETE /api/energy-records/{id}           # Supprimer
```

### Dashboard
```
GET    /api/category-subcategory-breakdown # Données agrégées par année/catégorie/sous-catégorie
```

**Documentation complète** : Consultez http://localhost:8000/docs (Swagger UI)

---

## Interface utilisateur

### Catégories - Couleurs du graphique
- Autres EnR: `#E74C3C` (Rouge)
- Biomasse: `#3498DB` (Bleu)
- Hydraulique: `#27AE60` (Vert)
- Récupération: `#F39C12` (Orange)
- Solaire: `#9B59B6` (Violet)
- Éolien: `#1ABC9C` (Turquoise)

### Accessibilité
- ✅ WCAG 2.1
- ✅ Contraste texte conforme
- ✅ Navigation au clavier
- ✅ Aria labels complets
- ✅ Focus visible

---

## Configuration

### Variables d'environnement
Créez un fichier `.env` à la racine :

```env
# PostgreSQL
POSTGRES_USER=energy_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=energy_monitoring
POSTGRES_HOST=db

# FastAPI
API_TITLE=Energy Monitoring API
API_VERSION=1.0.0
DEBUG=False
```

### Docker Compose
Le fichier `docker-compose.yml` définit :
- Service FastAPI (port 8000)
- Service PostgreSQL (port 5432)
- Volume persistant pour la DB
- Network custom

---

## Données d'exemple

L'application initialise automatiquement 34 enregistrements de test :
- 6 catégories
- 2-5 sous-catégories par catégorie
- 3 années : 2023, 2024, 2025
- Valeurs réalistes (kWh)

**Réinitialisez les données** :
```bash
docker compose down -v  # Supprime le volume
docker compose up       # Recrée avec données initiales
```

---

## Dépannage

### Port 8000 déjà utilisé
```bash
# Changer le port dans docker-compose.yml
ports:
  - "8080:8000"  # Utiliser 8080 au lieu de 8000
```

### Erreur de connexion à la base de données
```bash
# Vérifier les logs
docker compose logs db

# Redémarrer les services
docker compose restart
```

### Base de données corrompue
```bash
# Réinitialiser complètement
docker compose down -v
docker compose up --build
```

---

## Licence

MIT License - Libre d'utilisation

---

## Développement

### Setup local (sans Docker)
```bash
# Créer un venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer PostgreSQL localement
# ... (instructions spécifiques à votre système)

# Lancer FastAPI
uvicorn app.main:app --reload --port 8000
```

### Ajouter une nouvelle catégorie d'énergie
1. Ajouter via le formulaire (`/form` → bouton "Nouvelle catégorie")
2. Ou directement via API :
```bash
curl -X POST http://localhost:8000/api/categories \
  -H "Content-Type: application/json" \
  -d '{"name": "Géothermie", "description": "..."}'
```

---

## Support

Pour des questions ou problèmes :
- Consultez la page API (`/docs`)
- Vérifiez les logs Docker : `docker compose logs -f`
- Vérifiez les erreurs (F12) sur le frontend
- Vérifiez les documentations au format .md
- Ouvrez une issue sur GitHub

---

**Dernière mise à jour** : 15 janvier 2026
**Version** : 1.0.0
