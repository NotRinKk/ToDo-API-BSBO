from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import Task
from database import get_async_session
from datetime import date
from typing import List, Dict, Any

router = APIRouter(
    prefix="/stats",
    tags=["statistics"]
)

@router.get("/", response_model=dict)
async def get_tasks_stats(db: AsyncSession = Depends(get_async_session)) -> dict:
    result = await db.execute(select(Task))
    tasks = result.scalars().all()
    total_tasks = len(tasks)
    by_quadrant = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
    by_status = {"completed": 0, "pending": 0}

    for task in tasks:
        if task.quadrant in by_quadrant:
            by_quadrant[task.quadrant] += 1
        if task.completed:
            by_status["completed"] += 1
        else:
            by_status["pending"] += 1
            
    return {
        "total_tasks": total_tasks,
        "by_quadrant": by_quadrant,
        "by_status": by_status
    }

@router.get("/deadlines", response_model=List[Dict[str, Any]])
async def get_pending_tasks_deadlines(
    db: AsyncSession = Depends(get_async_session)
) -> List[Dict[str, Any]]:
    """Получить статистику по срокам выполнения невыполненных задач"""
    result = await db.execute(
        select(Task).where(Task.completed == False).where(Task.deadline_at.isnot(None))
    )
    tasks = result.scalars().all()
    
    deadlines_info = []
    today = date.today()
    
    for task in tasks:
        days_until_deadline = (task.deadline_at - today).days
        
        deadlines_info.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "created_at": task.created_at,
            "deadline_at": task.deadline_at,
            "days_until_deadline": days_until_deadline,
            "is_urgent": days_until_deadline <= 3,
            "quadrant": task.quadrant
        })
    
    # Сортируем по оставшемуся времени (сначала самые срочные)
    deadlines_info.sort(key=lambda x: x["days_until_deadline"])
    
    return deadlines_info