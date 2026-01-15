# Database Schema

Ce projet utilise **PostgreSQL** (par défaut) via **SQLAlchemy ORM**.

- Fichier de connexion : `app/database.py`
- Modèles ORM : `app/models.py`
- Tables principales : `categories`, `subcategories`, `energy_records`

---

## 1) Diagramme ER (Entity–Relationship)

```mermaid
erDiagram
    CATEGORIES ||--o{ SUBCATEGORIES : "contient"
    CATEGORIES ||--o{ ENERGY_RECORDS : "regroupe"
    SUBCATEGORIES ||--o{ ENERGY_RECORDS : "détaille"

    CATEGORIES {
        int id PK
        string name "unique"
        string description "nullable"
        datetime created_at "default now()"
    }

    SUBCATEGORIES {
        int id PK
        string name
        string description "nullable"
        int category_id FK
        datetime created_at "default now()"
    }

    ENERGY_RECORDS {
        int id PK
        int year
        numeric value_kwh "Numeric(14,2)"
        int category_id FK
        int subcategory_id FK
        datetime created_at "default now()"
    }
````

---

## 2) Description des tables

### Table `categories`

Stocke les catégories d’énergie (ex: Électricité, Gaz, etc.).

| Champ         | Type         | Null | Détails                           |
| ------------- | ------------ | ---- | --------------------------------- |
| `id`          | int          | non  | PK                                |
| `name`        | varchar(100) | non  | **Unique** (`uq_categories_name`) |
| `description` | varchar(255) | oui  | Description optionnelle           |
| `created_at`  | datetime tz  | non  | `server_default = now()`          |

---

### Table `subcategories`

Sous-catégories rattachées à une catégorie (ex: “Chauffage”, “ECS”, “Éclairage”…).

| Champ         | Type         | Null | Détails                  |
| ------------- | ------------ | ---- | ------------------------ |
| `id`          | int          | non  | PK                       |
| `name`        | varchar(100) | non  | Unique **par catégorie** |
| `description` | varchar(255) | oui  | Optionnel                |
| `category_id` | int          | non  | FK → `categories.id`     |
| `created_at`  | datetime tz  | non  | `server_default = now()` |

**Contrainte d’unicité :**

* (`name`, `category_id`) unique (`uq_subcategories_name_category`)

---

### Table `energy_records`

Enregistre la consommation annuelle (kWh) par catégorie et sous-catégorie.

| Champ            | Type          | Null | Détails                  |
| ---------------- | ------------- | ---- | ------------------------ |
| `id`             | int           | non  | PK                       |
| `year`           | int           | non  | Année (ex: 2026)         |
| `value_kwh`      | numeric(14,2) | non  | Valeur en kWh            |
| `category_id`    | int           | non  | FK → `categories.id`     |
| `subcategory_id` | int           | non  | FK → `subcategories.id`  |
| `created_at`     | datetime tz   | non  | `server_default = now()` |

---

## 3) Relations, intégrité et règles

### Relations

* `categories (1) → (N) subcategories`
* `categories (1) → (N) energy_records`
* `subcategories (1) → (N) energy_records`

### Suppression en cascade (ORM)

Les relations sont déclarées avec `cascade="all,delete"` côté ORM :

* Si une **Category** est supprimée → ses **SubCategory** et ses **EnergyRecord** sont supprimés côté ORM.
* Si une **SubCategory** est supprimée → ses **EnergyRecord** sont supprimés côté ORM.

> Note : selon la configuration DB, ces cascades peuvent être appliquées au niveau ORM uniquement (pas forcément via `ON DELETE CASCADE` en base).

### Contraintes d’unicité

* `categories.name` unique
* `subcategories.(name, category_id)` unique

---

## 4) Modèle hiérarchique (logique métier)

Le modèle est naturellement hiérarchique :

* **Category**

  * **SubCategory**

    * **EnergyRecord** (par `year`)

Même si `energy_records` référence à la fois `category_id` et `subcategory_id`, l’intention est :

* une sous-catégorie appartient à une catégorie,
* un record décrit une sous-catégorie (et donc sa catégorie).

---

## 5) Exemples de données

### Insertion de base

```sql
-- Catégorie
INSERT INTO categories (name, description)
VALUES ('Electricité', 'Consommation électrique globale');

-- Sous-catégories
INSERT INTO subcategories (name, description, category_id)
VALUES
  ('Chauffage', 'Chauffage électrique', 1),
  ('Eclairage', 'Éclairage intérieur', 1);

-- Records annuels
INSERT INTO energy_records (year, value_kwh, category_id, subcategory_id)
VALUES
  (2025, 12450.50, 1, 1),
  (2025,  2150.00, 1, 2);
```

---

## 6) Agrégations & calculs utiles

### Total kWh par année

```sql
SELECT year, SUM(value_kwh) AS total_kwh
FROM energy_records
GROUP BY year
ORDER BY year;
```

### Total kWh par catégorie (pour une année)

```sql
SELECT c.name AS category, er.year, SUM(er.value_kwh) AS total_kwh
FROM energy_records er
JOIN categories c ON c.id = er.category_id
WHERE er.year = 2025
GROUP BY c.name, er.year
ORDER BY total_kwh DESC;
```

### Détail par sous-catégorie (pour une catégorie + année)

```sql
SELECT sc.name AS subcategory, er.year, SUM(er.value_kwh) AS total_kwh
FROM energy_records er
JOIN subcategories sc ON sc.id = er.subcategory_id
WHERE er.category_id = 1 AND er.year = 2025
GROUP BY sc.name, er.year
ORDER BY total_kwh DESC;
```

### Part (%) par sous-catégorie sur une année

```sql
WITH totals AS (
  SELECT year, SUM(value_kwh) AS total_kwh
  FROM energy_records
  WHERE year = 2025
  GROUP BY year
)
SELECT
  sc.name,
  SUM(er.value_kwh) AS kwh,
  ROUND(100.0 * SUM(er.value_kwh) / t.total_kwh, 2) AS pct
FROM energy_records er
JOIN subcategories sc ON sc.id = er.subcategory_id
JOIN totals t ON t.year = er.year
WHERE er.year = 2025
GROUP BY sc.name, t.total_kwh
ORDER BY pct DESC;
```

---

**Dernière mise à jour** : 15 janvier 2026 
**API Version** : 1.0.0