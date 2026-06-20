"""
Component Repository - Database operations for component library
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.electronics_intelligence.models.sqlalchemy_models import ComponentLibrary


class ComponentRepository:
    """Repository for ComponentLibrary"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_all(self):
        result = await self.db.execute(select(ComponentLibrary))
        return result.scalars().all()
        
    async def get_by_id(self, component_id: str):
        result = await self.db.execute(
            select(ComponentLibrary).where(ComponentLibrary.id == component_id)
        )
        return result.scalar_one_or_none()
        
    async def get_by_type(self, component_type: str):
        result = await self.db.execute(
            select(ComponentLibrary).where(ComponentLibrary.component_type == component_type)
        )
        return result.scalars().all()
