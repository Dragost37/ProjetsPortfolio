# API Documentation

Documentation complète de l'API REST du Tableau de Bord Énergétique.

**URL de base** : `http://localhost:8000`  
**Format** : JSON  
**Authentification** : Aucune (application interne)

---

## Démarrage rapide

### Accéder à la documentation interactive
- **Swagger UI** : http://localhost:8000/docs

### Exemple de requête simple
```bash
curl -X GET "http://localhost:8000/api/categories" \
  -H "accept: application/json"
```

---

## 📑 Table des matières

- [Catégories](#catégories)
- [Sous-catégories](#sous-catégories)
- [Enregistrements](#enregistrements)
- [Dashboard](#dashboard)
- [Codes d'erreur](#codes-derreur)
- [Exemples complets](#exemples-complets)

---

## Catégories

### GET /api/categories
Liste toutes les catégories d'énergie.

**Paramètres** : Aucun

**Réponse** (200 OK) :
```json
[
  {
    "id": 1,
    "name": "Solaire",
    "description": "Énergie solaire"
  },
  {
    "id": 2,
    "name": "Éolien",
    "description": "Énergie éolienne"
  }
]
```

---

### POST /api/categories
Crée une nouvelle catégorie avec ses sous-catégories.

**Body** (application/json) :
```json
{
  "name": "Géothermie",
  "description": "Énergie géothermique",
  "subcategories": [
    "Géothermie haute température",
    "Géothermie basse température"
  ]
}
```

**Paramètres** :
| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `name` | string | ✅ | Nom de la catégorie (unique) |
| `description` | string | ❌ | Description optionnelle |
| `subcategories` | array | ✅ | Minimum 1 sous-catégorie |

**Réponse** (200 OK) :
```json
{
  "id": 7,
  "name": "Géothermie",
  "description": "Énergie géothermique"
}
```

**Codes d'erreur** :
- `400` : `name` ou `subcategories` manquants/vides
- `409` : Catégorie déjà existante

---

## Sous-catégories

### GET /api/subcategories
Liste les sous-catégories, optionnellement filtrées par catégorie.

**Paramètres** :
| Nom | Type | Obligatoire | Description |
|-----|------|-------------|-------------|
| `category_id` | integer | ❌ | Filtrer par ID de catégorie |

**Exemple** :
```bash
GET /api/subcategories?category_id=1
```

**Réponse** (200 OK) :
```json
[
  {
    "id": 1,
    "name": "Photovoltaïque",
    "description": null
  },
  {
    "id": 2,
    "name": "Solaire thermique",
    "description": null
  }
]
```

---

### POST /api/subcategories
Ajoute une sous-catégorie à une catégorie existante.

**Body** (application/json) :
```json
{
  "category_id": 1,
  "name": "Panneaux solaires bifaciaux"
}
```

**Paramètres** :
| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `category_id` | integer | ✅ | ID de la catégorie |
| `name` | string | ✅ | Nom de la sous-catégorie |

**Réponse** (200 OK) :
```json
{
  "id": 15,
  "name": "Panneaux solaires bifaciaux",
  "category_id": 1
}
```

**Codes d'erreur** :
- `400` : `category_id` ou `name` manquants
- `404` : Catégorie non trouvée
- `409` : Sous-catégorie déjà existante

---

## Enregistrements

### POST /records
Crée un nouvel enregistrement de consommation énergétique.

**Content-Type** : `application/x-www-form-urlencoded`

**Paramètres** (Form Data) :
| Nom | Type | Obligatoire | Description |
|-----|------|-------------|-------------|
| `year` | integer | ✅ | Année (ex: 2025) |
| `category_id` | integer | ✅ | ID de la catégorie |
| `subcategory_id` | integer | ✅ | ID de la sous-catégorie |
| `value_kwh` | float | ✅ | Consommation en kWh |

**Exemple cURL** :
```bash
curl -X POST "http://localhost:8000/records" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "year=2025&category_id=1&subcategory_id=1&value_kwh=5000.50"
```

**Réponse** (200 OK) :
```json
{
  "message": "Enregistrement créé avec succès"
}
```

**Codes d'erreur** :
- `400` : Paramètre obligatoire manquant
- `404` : Catégorie ou sous-catégorie non trouvée

---

## Dashboard

### GET /api/category-subcategory-breakdown
Récupère les données agrégées pour le dashboard.

Structure : Pour chaque année, pour chaque catégorie, la liste des sous-catégories avec leurs valeurs totales.

**Paramètres** : Aucun

**Réponse** (200 OK) :
```json
{
  "2023": {
    "Solaire": {
      "Photovoltaïque": 4500.5,
      "Solaire thermique": 2100.25
    },
    "Éolien": {
      "Éolien terrestre": 6200.0,
      "Éolien offshore": 3400.75
    }
  },
  "2024": {
    "Solaire": {
      "Photovoltaïque": 5100.0,
      "Solaire thermique": 2450.50
    }
  },
  "2025": {
    "Solaire": {
      "Photovoltaïque": 5800.25,
      "Solaire thermique": 2750.75
    }
  }
}
```

**Cas d'usage** : 
- Chargé au démarrage du dashboard
- Utilisé pour afficher le détail au survol des barres du graphique
- Structure imbriquée pour accès facile: `data[year][category][subcategory]`

---

## Codes d'erreur

### Erreurs courantes

| Code | Signification | Exemple |
|------|---------------|---------|
| `200` | ✅ Succès | Requête traitée correctement |
| `400` | ❌ Mauvaise requête | Paramètre obligatoire manquant |
| `404` | ❌ Non trouvé | Catégorie/sous-catégorie inexistante |
| `409` | ❌ Conflit | Ressource déjà existante |
| `500` | ❌ Erreur serveur | Erreur non gérée en base de données |

### Format d'erreur
```json
{
  "detail": "Description de l'erreur"
}
```

---

## Exemples complets

### Exemple 1 : Créer une catégorie complète

```bash
# 1. Créer la catégorie avec sous-catégories
curl -X POST "http://localhost:8000/api/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marémotrice",
    "description": "Énergie marémotrice et houlomotrice",
    "subcategories": ["Marée", "Houle", "Courant marin"]
  }'

# Réponse: {"id": 8, "name": "Marémotrice", ...}

# 2. Ajouter un enregistrement pour cette catégorie
curl -X POST "http://localhost:8000/records" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "year=2025&category_id=8&subcategory_id=22&value_kwh=1500.00"

# Réponse: {"message": "Enregistrement créé avec succès"}
```

### Exemple 2 : Récupérer et traiter les données du dashboard

```javascript
// Fetch data
fetch('/api/category-subcategory-breakdown')
  .then(r => r.json())
  .then(data => {
    // Accéder aux données imbriquées
    const solaire2025 = data["2025"]["Solaire"];
    console.log("Photovoltaïque 2025:", solaire2025["Photovoltaïque"]); // 5800.25
    
    // Itérer sur toutes les années
    Object.entries(data).forEach(([year, categories]) => {
      console.log(`Année ${year}`);
      Object.entries(categories).forEach(([cat, subcats]) => {
        const total = Object.values(subcats).reduce((a,b) => a+b, 0);
        console.log(`  ${cat}: ${total} kWh`);
      });
    });
  });
```

### Exemple 3 : Ajouter une sous-catégorie à une catégorie existante

```bash
# Ajouter à la catégorie Solaire (id=1)
curl -X POST "http://localhost:8000/api/subcategories" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 1,
    "name": "Solaire concentré"
  }'

# Réponse: {"id": 16, "name": "Solaire concentré", "category_id": 1}
```

### Exemple 4 : Filtrer les sous-catégories

```bash
# Récupérer uniquement les sous-catégories de Biomasse (id=4)
curl -X GET "http://localhost:8000/api/subcategories?category_id=4"

# Réponse:
# [
#   {"id": 7, "name": "Bagasse", ...},
#   {"id": 8, "name": "Bois", ...},
#   {"id": 9, "name": "Biogaz", ...}
# ]
```

---

# Intégration Frontend

### JavaScript - Créer une catégorie depuis un formulaire

```javascript
async function createCategory(name, description, subcategories) {
  const response = await fetch('/api/categories', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: name,
      description: description,
      subcategories: subcategories
    })
  });
  
  if (response.ok) {
    const data = await response.json();
    console.log('Catégorie créée:', data);
    return data;
  } else {
    const error = await response.json();
    console.error('Erreur:', error.detail);
  }
}

// Utilisation
createCategory(
  'Énergie marine',
  'Sources d\'énergie marines',
  ['Marée', 'Houle']
);
```

### Python - Requête avec requests

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Créer une catégorie
response = requests.post(
    f"{BASE_URL}/api/categories",
    json={
        "name": "Fusion",
        "description": "Énergie de fusion nucléaire",
        "subcategories": ["Fusion magnétique", "Fusion par inertie"]
    }
)
print(response.json())

# Créer un enregistrement
response = requests.post(
    f"{BASE_URL}/records",
    data={
        "year": 2025,
        "category_id": 1,
        "subcategory_id": 1,
        "value_kwh": 4500.50
    }
)
print(response.json())

# Récupérer les données dashboard
response = requests.get(f"{BASE_URL}/api/category-subcategory-breakdown")
data = response.json()
print(f"Solaire 2025: {data['2025']['Solaire']}")
```

---

## Status & Monitoring

### Health Check
```bash
curl -X GET "http://localhost:8000/"
# Redirect vers /form (l'app fonctionne)
```

### Version
Visible dans la documentation Swagger à http://localhost:8000/docs

---

## Notes de sécurité

⚠️ **IMPORTANT** : Cette API n'a **pas d'authentification**.

Pour la production :
- ✅ Ajouter OAuth2 / JWT
- ✅ Valider les inputs côté serveur (CSRF)
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ HTTPS obligatoire
- ✅ Logs d'audit

---

## Support

Pour des questions :
1. Consultez la documentation Swagger : `/docs`
2. Vérifiez les exemples ci-dessus
3. Ouvrez une issue sur GitHub

---

**Dernière mise à jour** : 15 janvier 2026  
**API Version** : 1.0.0
