from fastapi import APIRouter, HTTPException, Query, Response
from typing import List, Dict, Any
from datetime import datetime
from database_copy import tasks_db

router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    responses={404: {"description": "Task not found"}},
)

@router.get("")
async def get_all_tasks() -> dict:
    return {
        "count": len(tasks_db), # считает количество записей в хранилище
        "tasks": tasks_db # выводит всё, чта есть в хранилище
    }


q1 = "Q1"
q2 = "Q2"
q3 = "Q3"
q4 = "Q4"

@router.get("/stats")
async def get_tasks_stats() -> dict:
    total_tasks = 0
    tasks_q1 = 0
    tasks_q2 = 0
    tasks_q3 = 0
    tasks_q4 = 0
    completed_tasks = 0
    for task in tasks_db:
        total_tasks += 1
        if task["quadrant"] == q1:
            tasks_q1 += 1
        elif task["quadrant"] == q2:
            tasks_q2 += 1
        elif task["quadrant"] == q3:
            tasks_q3 += 1
        elif task["quadrant"] == q4:
            tasks_q4 += 1
        
        if task["completed"] == True:
            completed_tasks += 1
    
    return {
        "total_tasks" : total_tasks,
        "by_quadrant" : {
            "Q1" : tasks_q1,
            "Q2" : tasks_q2,
            "Q3" : tasks_q3,
            "Q4" : tasks_q4
        },
        "by_status" : {
            "completed" : completed_tasks,
            "pending" : (total_tasks - completed_tasks)
        }
    }

@router.get("/status/{status}")
async def get_tasks_by_status(status: str) -> dict:
    if status not in ["completed", "pending"]:
        raise HTTPException( 
            status_code=400,
            detail="Неверный статус"
        )
    if status == "completed":
        filtered_tasks = [
            task 
            for task in tasks_db 
            if task["completed"] == True 
        ]
    else:
        filtered_tasks = [
            task 
            for task in tasks_db 
            if task["completed"] == False 
        ]
    return {
        "status": status,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    } 