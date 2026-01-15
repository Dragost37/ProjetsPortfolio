from sqlalchemy.orm import Session
from sqlalchemy import select, func
from .models import Category, SubCategory, EnergyRecord

def delete_record(db: Session, record_id: int) -> bool:
    """Delete an energy record by ID. Returns True if deleted, False if not found."""
    rec = db.scalar(select(EnergyRecord).where(EnergyRecord.id == record_id))
    if not rec:
        return False
    db.delete(rec)
    db.commit()
    return True

def normalize_name(name: str) -> str:
    return " ".join(name.strip().split())

# Categories
def create_category(db: Session, name: str, description: str | None):
    name_norm = normalize_name(name)
    existing = db.scalar(select(Category).where(func.lower(Category.name) == name_norm.lower()))
    if existing:
        return None  # already exists
    cat = Category(name=name_norm, description=description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat

def list_categories(db: Session):
    return db.scalars(select(Category).order_by(Category.name.asc())).all()

def get_category(db: Session, category_id: int):
    """Get a single category by ID"""
    return db.scalar(select(Category).where(Category.id == category_id))

def create_subcategory(db: Session, name: str, description: str | None, category_id: int):
    name_norm = normalize_name(name)
    existing = db.scalar(select(SubCategory).where(
        (func.lower(SubCategory.name) == name_norm.lower()) & 
        (SubCategory.category_id == category_id)
    ))
    if existing:
        return None
    subcat = SubCategory(name=name_norm, description=description, category_id=category_id)
    db.add(subcat)
    db.commit()
    db.refresh(subcat)
    return subcat

def list_subcategories(db: Session, category_id: int | None = None):
    stmt = select(SubCategory).order_by(SubCategory.name.asc())
    if category_id:
        stmt = stmt.where(SubCategory.category_id == category_id)
    return db.scalars(stmt).all()

# Records
def create_record(db: Session, year: int, value_kwh: float, category_id: int, subcategory_id: int):
    """Create energy record - subcategory_id is now required"""
    rec = EnergyRecord(year=year, value_kwh=value_kwh, category_id=category_id, subcategory_id=subcategory_id)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def list_records(db: Session, category_id: int | None = None, year: int | None = None):
    stmt = select(EnergyRecord)

    if category_id:
        stmt = stmt.where(EnergyRecord.category_id == category_id)

    if year:
        stmt = stmt.where(EnergyRecord.year == year)

    stmt = stmt.order_by(EnergyRecord.year.asc(), EnergyRecord.id.desc())
    return db.scalars(stmt).all()

def list_years(db: Session, category_id: int | None = None):
    stmt = select(EnergyRecord.year).distinct().order_by(EnergyRecord.year.asc())
    if category_id:
        stmt = stmt.where(EnergyRecord.category_id == category_id)
    return [y for (y,) in db.execute(stmt).all()]

def get_dashboard_stats(db: Session, category_id: int | None = None):
    stmt = select(
        func.coalesce(func.sum(EnergyRecord.value_kwh), 0),
        func.coalesce(func.avg(EnergyRecord.value_kwh), 0),
        func.count(EnergyRecord.id),
    )
    if category_id:
        stmt = stmt.where(EnergyRecord.category_id == category_id)
    total, avg, count = db.execute(stmt).one()
    return float(total), float(avg), int(count)

def get_yearly_series(db: Session, category_id: int | None = None):
    stmt = select(
        EnergyRecord.year,
        func.sum(EnergyRecord.value_kwh).label("sum_kwh"),
    ).group_by(EnergyRecord.year).order_by(EnergyRecord.year.asc())
    if category_id:
        stmt = stmt.where(EnergyRecord.category_id == category_id)
    rows = db.execute(stmt).all()
    years = [r[0] for r in rows]
    values = [float(r[1]) for r in rows]
    return years, values

def get_stacked_yearly_series(db: Session):
    """Get yearly energy data grouped by category for stacked bar chart"""
    stmt = select(
        EnergyRecord.year,
        Category.name,
        Category.id,
        func.sum(EnergyRecord.value_kwh).label("sum_kwh"),
    ).join(Category).group_by(
        EnergyRecord.year, Category.id, Category.name
    ).order_by(EnergyRecord.year.asc(), Category.name.asc())
    
    rows = db.execute(stmt).all()
    
    if not rows:
        return [], []
    
    # Build structure: { year: { category_name: value, ... }, ... }
    data = {}
    categories_set = set()
    
    for year, cat_name, cat_id, sum_kwh in rows:
        if year not in data:
            data[year] = {}
        data[year][cat_name] = float(sum_kwh)
        categories_set.add(cat_name)
    
    # Get all years sorted
    years = sorted(data.keys())
    categories = sorted(list(categories_set))
    
    # Build datasets for each category
    datasets = []
    # Color palette
    colors = [
        'rgba(231, 76, 60, 0.7)',       # Rouge Énergie
        'rgba(52, 152, 219, 0.7)',      # Bleu
        'rgba(39, 174, 96, 0.7)',       # Vert
        'rgba(243, 156, 18, 0.7)',      # Orange
        'rgba(155, 89, 182, 0.7)',      # Violet
        'rgba(26, 188, 156, 0.7)',      # Turquoise
        'rgba(230, 126, 34, 0.7)',      # Orange foncé
        'rgba(52, 73, 94, 0.7)',        # Gris bleu
        'rgba(44, 62, 80, 0.7)',        # Noir bleu
        'rgba(241, 196, 15, 0.7)',      # Jaune
    ]
    
    for idx, cat_name in enumerate(categories):
        values = [data[year].get(cat_name, 0) for year in years]
        datasets.append({
            'label': cat_name,
            'data': values,
            'backgroundColor': colors[idx % len(colors)],
            'borderColor': colors[idx % len(colors)].replace('0.7', '1'),
            'borderWidth': 1
        })
    
    return years, datasets
