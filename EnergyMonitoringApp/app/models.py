from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("name", name="uq_categories_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subcategories = relationship("SubCategory", back_populates="category", cascade="all,delete")
    records = relationship("EnergyRecord", back_populates="category", cascade="all,delete")

class SubCategory(Base):
    __tablename__ = "subcategories"
    __table_args__ = (UniqueConstraint("name", "category_id", name="uq_subcategories_name_category"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category", back_populates="subcategories")
    records = relationship("EnergyRecord", back_populates="subcategory", cascade="all,delete")

class EnergyRecord(Base):
    __tablename__ = "energy_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    value_kwh: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategories.id"), nullable=False)
    
    category = relationship("Category", back_populates="records")
    subcategory = relationship("SubCategory", back_populates="records")

    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
