from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Product, Sale, Category
from auth_utils import get_current_user

router = APIRouter()

@router.get("/summary")
async def dashboard_summary(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    total_products = await db.scalar(select(func.count(Product.id)))
    total_stock_value = await db.scalar(select(func.sum(Product.unit_price * Product.stock_qty)))
    total_revenue = await db.scalar(select(func.sum(Sale.total)))

    cat_result = await db.execute(
        select(Category.name, func.sum(Product.stock_qty).label("total_stock"))
        .join(Product, Product.category_id == Category.id)
        .group_by(Category.name)
    )
    category_breakdown = [{"category": r[0], "total_stock": r[1]} for r in cat_result]

    return {
        "total_products": total_products or 0,
        "total_stock_value": float(total_stock_value or 0),
        "total_revenue": float(total_revenue or 0),
        "category_breakdown": category_breakdown
    }
