from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import date
from database import get_db
from models import Sale, Product
from auth_utils import get_current_user
import uuid

router = APIRouter()

class SaleCreate(BaseModel):
    product_id: uuid.UUID
    quantity: int

@router.post("/")
async def record_sale(body: SaleCreate, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):
    result = await db.execute(select(Product).where(Product.id == body.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock_qty < body.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    product.stock_qty -= body.quantity
    total = float(product.unit_price) * body.quantity
    sale = Sale(
        product_id=body.product_id,
        quantity=body.quantity,
        unit_price=product.unit_price,
        total=total,
        sold_by=uuid.UUID(user_id)
    )
    db.add(sale)
    await db.commit()
    await db.refresh(sale)
    return sale

@router.get("/")
async def list_sales(product_id: Optional[uuid.UUID] = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    q = select(Sale)
    if product_id:
        q = q.where(Sale.product_id == product_id)
    result = await db.execute(q.order_by(Sale.sold_at.desc()))
    return result.scalars().all()
