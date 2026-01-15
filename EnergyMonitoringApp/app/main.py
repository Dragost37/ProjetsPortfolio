from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi import Query

from .database import Base, engine, get_db
from . import crud

# Create tables (simple setup for test technique)
Base.metadata.create_all(bind=engine)

# Pre-populate with energy categories
def init_categories():
    """Initialize database with energy categories, subcategories, and sample data"""
    db = next(get_db())
    try:
        # Check if categories already exist
        existing_cats = crud.list_categories(db)
        if existing_cats:
            return
        
        # Define categories with subcategories
        categories_data = {
            "Solaire": {
                "description": "Énergie solaire",
                "subcategories": ["Photovoltaïque", "Solaire thermique"]
            },
            "Éolien": {
                "description": "Énergie éolienne",
                "subcategories": ["Éolien terrestre", "Éolien offshore"]
            },
            "Hydraulique": {
                "description": "Énergie hydraulique",
                "subcategories": ["Hydraulique au fil de l'eau", "Hydraulique de lac", "Hydraulique au remontée"]
            },
            "Biomasse": {
                "description": "Énergie issue de la biomasse",
                "subcategories": ["Bagasse", "Bois", "Biogaz", "Bioéthanol", "Bioliquide"]
            },
            "Autres EnR": {
                "description": "Autres énergies renouvelables et émergentes",
                "subcategories": ["Géothermie", "ETM", "Houlomotrice", "ORC"]
            },
            "Récupération": {
                "description": "Récupération et valorisation d'énergie",
                "subcategories": ["Huiles usagées", "CSR", "Chaleur fatale", "Récupération thermique"]
            }
        }
        
        # Create categories and subcategories
        cat_map = {}  # Map category names to their objects
        subcat_map = {}  # Map (category_name, subcat_name) to subcategory objects
        
        for cat_name, cat_data in categories_data.items():
            cat = crud.create_category(db, name=cat_name, description=cat_data.get("description"))
            if cat:
                cat_map[cat_name] = cat
                if cat_data.get("subcategories"):
                    for subcat_name in cat_data["subcategories"]:
                        subcat = crud.create_subcategory(db, name=subcat_name, description=None, category_id=cat.id)
                        if subcat:
                            subcat_map[(cat_name, subcat_name)] = subcat
        
        # Add sample energy records
        sample_records = [
            # 2023 data
            (2023, "Solaire", "Photovoltaïque", 4500.50),
            (2023, "Solaire", "Solaire thermique", 2100.75),
            (2023, "Éolien", "Éolien terrestre", 8900.00),
            (2023, "Éolien", "Éolien offshore", 5600.25),
            (2023, "Hydraulique", "Hydraulique au fil de l'eau", 12300.00),
            (2023, "Hydraulique", "Hydraulique de lac", 8700.50),
            (2023, "Biomasse", "Bagasse", 3200.00),
            (2023, "Biomasse", "Bois", 1800.75),
            (2023, "Autres EnR", "Géothermie", 2500.00),
            (2023, "Récupération", "Chaleur fatale", 1500.25),
            
            # 2024 data
            (2024, "Solaire", "Photovoltaïque", 5200.75),
            (2024, "Solaire", "Solaire thermique", 2450.00),
            (2024, "Éolien", "Éolien terrestre", 9500.50),
            (2024, "Éolien", "Éolien offshore", 6100.00),
            (2024, "Hydraulique", "Hydraulique au fil de l'eau", 13200.00),
            (2024, "Hydraulique", "Hydraulique de lac", 9300.75),
            (2024, "Biomasse", "Bagasse", 3800.00),
            (2024, "Biomasse", "Biogaz", 2100.50),
            (2024, "Autres EnR", "Géothermie", 2800.00),
            (2024, "Autres EnR", "ETM", 1200.75),
            (2024, "Récupération", "Chaleur fatale", 1800.00),
            (2024, "Récupération", "CSR", 950.25),
            
            # 2025 data
            (2025, "Solaire", "Photovoltaïque", 5850.00),
            (2025, "Solaire", "Solaire thermique", 2700.50),
            (2025, "Éolien", "Éolien terrestre", 10200.00),
            (2025, "Éolien", "Éolien offshore", 6800.75),
            (2025, "Hydraulique", "Hydraulique au fil de l'eau", 14000.00),
            (2025, "Hydraulique", "Hydraulique de lac", 10100.25),
            (2025, "Biomasse", "Bagasse", 4200.00),
            (2025, "Biomasse", "Biogaz", 2400.75),
            (2025, "Autres EnR", "Géothermie", 3100.00),
            (2025, "Autres EnR", "ETM", 1500.50),
            (2025, "Autres EnR", "Houlomotrice", 800.00),
            (2025, "Récupération", "Chaleur fatale", 2100.00),
            (2025, "Récupération", "CSR", 1200.75),
            (2025, "Récupération", "Récupération thermique", 850.50),
        ]
        
        # Insert sample records
        for year, cat_name, subcat_name, value_kwh in sample_records:
            if cat_name in cat_map and (cat_name, subcat_name) in subcat_map:
                cat = cat_map[cat_name]
                subcat = subcat_map[(cat_name, subcat_name)]
                crud.create_record(db, year=year, value_kwh=value_kwh, category_id=cat.id, subcategory_id=subcat.id)
    finally:
        db.close()

init_categories()

app = FastAPI(
    title="Energy Monitoring API",
    description="API de suivi de consommation énergétique par source d'énergie - Réunion",
    version="1.0.0",
    contact={
        "name": "Support",
        "url": "https://github.com/Dragost37/ProjetsPortfolio",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Pages",
            "description": "Pages HTML de l'application web"
        },
        {
            "name": "Catégories",
            "description": "Gestion des catégories d'énergie (Solaire, Éolien, etc.)"
        },
        {
            "name": "Sous-catégories",
            "description": "Gestion des sous-catégories (Photovoltaïque, Éolien terrestre, etc.)"
        },
        {
            "name": "Enregistrements",
            "description": "Gestion des mesures de consommation énergétique"
        },
        {
            "name": "Dashboard",
            "description": "Données agrégées pour la visualisation"
        },
    ]
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Configure documentation UIs
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

@app.get("/docs", include_in_schema=False)
async def get_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Energy API - Swagger UI",
        oauth2_redirect_url="/docs/oauth2-redirect",
        swagger_ui_parameters={"defaultModelsExpandDepth": 1},
    )

@app.get("/redoc", include_in_schema=False)
async def get_redoc():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="Energy API - ReDoc",
    )

# ---------- Pages ----------
@app.get("/", response_class=HTMLResponse)
def home():
    return RedirectResponse(url="/form", status_code=303)

@app.get("/form", response_class=HTMLResponse)
def form_page(request: Request, db: Session = Depends(get_db)):
    categories = crud.list_categories(db)
    return templates.TemplateResponse("form.html", {"request": request, "categories": categories})

@app.post("/records")
def create_record(
    year: int = Form(...),
    category_id: int = Form(...),
    value_kwh: float = Form(...),
    subcategory_id: int = Form(...),
    db: Session = Depends(get_db),
):
    crud.create_record(db, year=year, value_kwh=value_kwh, category_id=category_id, subcategory_id=subcategory_id)
    return JSONResponse(status_code=200, content={"message": "Enregistrement créé avec succès"})

@app.get("/list", response_class=HTMLResponse)
def list_page(
    request: Request,
    category_id: str | None = Query(default=None),
    year: str | None = None,   # accepte 'all'
    db: Session = Depends(get_db),
):
    # --- conversion category_id (tolère category_id="") ---
    category_id_int: int | None = None
    if category_id and category_id.strip() != "":
        try:
            category_id_int = int(category_id)
        except ValueError:
            category_id_int = None

    categories = crud.list_categories(db)
    years = crud.list_years(db, category_id=category_id_int)

    # valeur affichée dans le select
    selected_year = year if year is not None else "all"

    # valeur utilisée pour filtrer en DB
    year_int: int | None = None
    if year and year != "all":
        try:
            year_int = int(year)
        except ValueError:
            year_int = None
            selected_year = "all"

    records = crud.list_records(db, category_id=category_id_int, year=year_int)

    cat_map = {c.id: c.name for c in categories}

    rows = []
    for r in records:
        rows.append({
            "id": r.id,
            "year": r.year,
            "value_kwh": float(r.value_kwh),
            "category": cat_map.get(r.category_id, "?"),
            "subcategory": r.subcategory.name if r.subcategory else None
        })

    return templates.TemplateResponse(
        "list.html",
        {
            "request": request,
            "categories": categories,
            "years": years,
            "rows": rows,
            "selected_category_id": category_id_int,
            "selected_year": selected_year,
        },
    )

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, category_id: int | None = None, db: Session = Depends(get_db)):
    categories = crud.list_categories(db)
    total, avg, count = crud.get_dashboard_stats(db, category_id=category_id)
    
    # Get both simple series (for single category view) and stacked series (for all categories)
    years, values = crud.get_yearly_series(db, category_id=category_id)
    stacked_years, stacked_datasets = crud.get_stacked_yearly_series(db)
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "categories": categories,
            "selected_category_id": category_id,
            "total": total,
            "avg": avg,
            "count": count,
            "years": years,
            "values": values,
            "stacked_years": stacked_years,
            "stacked_datasets": stacked_datasets,
        },
    )


# ---------- JSON API (used by JS for category creation) ----------
@app.get("/api/categories", tags=["Catégories"])
def api_list_categories(db: Session = Depends(get_db)):
    """
    Liste toutes les catégories d'énergie disponibles.
    
    **Réponse** : Liste de catégories avec id, name, description
    """
    cats = crud.list_categories(db)
    return [{"id": c.id, "name": c.name, "description": c.description} for c in cats]

@app.post("/api/categories", tags=["Catégories"])
async def api_create_category(request: Request, db: Session = Depends(get_db)):
    """
    Crée une nouvelle catégorie avec ses sous-catégories.
    
    **Body** :
    - `name` : Nom de la catégorie (obligatoire)
    - `description` : Description (optionnel)
    - `subcategories` : Liste de noms de sous-catégories (minimum 1)
    
    **Réponse** : La catégorie créée ou erreur 409 si déjà existante
    """
    data = await request.json()
    name = (data.get("name") or "").strip()
    description = (data.get("description") or "").strip() or None
    subcategories = data.get("subcategories") or []

    if not name:
        raise HTTPException(status_code=400, detail="Le nom de la catégorie est obligatoire.")

    if not subcategories or len(subcategories) == 0:
        raise HTTPException(status_code=400, detail="Au moins une sous-catégorie est obligatoire.")

    cat = crud.create_category(db, name=name, description=description)
    if not cat:
        return JSONResponse(status_code=409, content={"detail": "Cette catégorie existe déjà."})

    for subcat_name in subcategories:
        subcat_name_clean = (subcat_name or "").strip()
        if subcat_name_clean:
            crud.create_subcategory(db, name=subcat_name_clean, description=None, category_id=cat.id)

    return {"id": cat.id, "name": cat.name, "description": cat.description}

@app.get("/api/subcategories", tags=["Sous-catégories"])
def api_list_subcategories(category_id: int | None = None, db: Session = Depends(get_db)):
    """
    Liste les sous-catégories.
    
    **Paramètres** :
    - `category_id` (optionnel) : Filtrer par catégorie
    
    **Réponse** : Liste de sous-catégories
    """
    subcats = crud.list_subcategories(db, category_id=category_id)
    return [{"id": sc.id, "name": sc.name, "description": sc.description} for sc in subcats]

@app.post("/api/subcategories", tags=["Sous-catégories"])
async def api_add_subcategory(request: Request, db: Session = Depends(get_db)):
    """
    Ajoute une sous-catégorie à une catégorie existante.
    
    **Body** :
    - `category_id` : ID de la catégorie (obligatoire)
    - `name` : Nom de la sous-catégorie (obligatoire)
    
    **Réponse** : La sous-catégorie créée ou erreur
    """
    data = await request.json()
    category_id = data.get("category_id")
    name = (data.get("name") or "").strip()

    if not category_id:
        raise HTTPException(status_code=400, detail="category_id est obligatoire.")
    if not name:
        raise HTTPException(status_code=400, detail="Le nom de la sous-catégorie est obligatoire.")

    cat = crud.get_category(db, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée.")

    subcat = crud.create_subcategory(db, name=name, description=None, category_id=category_id)
    if not subcat:
        return JSONResponse(status_code=409, content={"detail": "Cette sous-catégorie existe déjà."})

    return {"id": subcat.id, "name": subcat.name, "category_id": subcat.category_id}

@app.get("/api/category-subcategory-breakdown", tags=["Dashboard"])
def api_category_subcategory_breakdown(db: Session = Depends(get_db)):
    """
    Récupère les données agrégées par année, catégorie et sous-catégorie.
    
    Utilisé par le dashboard pour afficher le détail au survol.
    
    **Réponse** : Structure imbriquée { year: { category: { subcategory: value_kwh } } }
    """
    from sqlalchemy import select, func
    from .models import Category, SubCategory, EnergyRecord
    
    stmt = select(
        EnergyRecord.year,
        Category.name.label("category_name"),
        SubCategory.name.label("subcategory_name"),
        func.sum(EnergyRecord.value_kwh).label("total_kwh")
    ).join(
        Category, EnergyRecord.category_id == Category.id
    ).join(
        SubCategory, EnergyRecord.subcategory_id == SubCategory.id
    ).group_by(
        EnergyRecord.year, 
        Category.name, 
        SubCategory.name
    ).order_by(
        EnergyRecord.year.asc()
    )
    
    rows = db.execute(stmt).all()
    
    result = {}
    for row in rows:
        year_str = str(row.year)
        cat_name = row.category_name
        subcat_name = row.subcategory_name
        total_kwh = float(row.total_kwh) if row.total_kwh else 0.0
        
        if year_str not in result:
            result[year_str] = {}
        if cat_name not in result[year_str]:
            result[year_str][cat_name] = {}
        result[year_str][cat_name][subcat_name] = total_kwh
    
    return result

@app.post("/records/{record_id}/delete")
def delete_record(
    record_id: int,
    category_id: int | None = Form(default=None),
    year: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    ok = crud.delete_record(db, record_id=record_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Enregistrement introuvable.")

    url = "/list"
    params = []
    if category_id:
        params.append(f"category_id={category_id}")
    if year and year != "all":
        params.append(f"year={year}")
    if params:
        url += "?" + "&".join(params)

    return RedirectResponse(url=url, status_code=303)

@app.post("/api/subcategories")
async def api_add_subcategory(request: Request, db: Session = Depends(get_db)):
    """Add a subcategory to an existing category"""
    data = await request.json()
    category_id = data.get("category_id")
    name = (data.get("name") or "").strip()

    if not category_id:
        raise HTTPException(status_code=400, detail="category_id est obligatoire.")
    if not name:
        raise HTTPException(status_code=400, detail="Le nom de la sous-catégorie est obligatoire.")

    # Check if category exists
    cat = crud.get_category(db, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Catégorie non trouvée.")

    # Create subcategory
    subcat = crud.create_subcategory(db, name=name, description=None, category_id=category_id)
    if not subcat:
        return JSONResponse(status_code=409, content={"detail": "Cette sous-catégorie existe déjà."})

    return {"id": subcat.id, "name": subcat.name, "category_id": subcat.category_id}
