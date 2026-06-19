from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models import Product
from auth_utils import get_current_user
import uuid

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    category_id: int
    unit_price: float
    stock_qty: int = 0
    min_threshold: int = 5

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    unit_price: Optional[float] = None
    category_id: Optional[int] = None
    min_threshold: Optional[int] = None

class StockUpdate(BaseModel):
    stock_qty: int

@router.post("/")
async def create_product(body: ProductCreate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    product = Product(**body.dict())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

@router.get("/")
async def list_products(category: Optional[int] = None, search: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    q = select(Product)
    if category:
        q = q.where(Product.category_id == category)
    if search:
        q = q.where(Product.name.ilike(f"%{search}%"))
    result = await db.execute(q)
    return result.scalars().all()

@router.get("/alerts/low-stock")
async def low_stock(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Product).where(Product.stock_qty <= Product.min_threshold))
    return result.scalars().all()

@router.get("/{product_id}")
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}")
async def update_product(product_id: uuid.UUID, body: ProductUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for k, v in body.dict(exclude_none=True).items():
        setattr(product, k, v)
    await db.commit()
    await db.refresh(product)
    return product

@router.put("/{product_id}/stock")
async def update_stock(product_id: uuid.UUID, body: StockUpdate, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.stock_qty = body.stock_qty
    await db.commit()
    await db.refresh(product)
    return product

@router.delete("/{product_id}")
async def delete_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(product)
    await db.commit()
    return {"message": "Product deleted"}
