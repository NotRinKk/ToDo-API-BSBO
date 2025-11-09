from fastapi import APIRouter, HTTPException, Query, Response
from typing import List, Dict, Any
from datetime import datetime
from schemas import TaskBase, TaskCreate, TaskUpdate, TaskResponse
from database import tasks_db


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Task not found"}},
)

q1 = "Q1"
q2 = "Q2"
q3 = "Q3"
q4 = "Q4"

@router.get("/quadrant/{quadrant}")
async def get_tasks_by_quadrant(quadrant: str) -> dict:
    if quadrant not in ["Q1", "Q2", "Q3", "Q4"]:
        raise HTTPException( #специальный класс в FastAPI для возврата HTTP ошибок. Не забудьте добавть его вызов в 1 строке
            status_code=400,
            detail="Неверный квадрант. Используйте: Q1, Q2, Q3, Q4" #текст, который будет выведен пользователю
        )

    filtered_tasks = [
        task # ЧТО добавляем в список
        for task in tasks_db # ОТКУДА берем элементы
        if task["quadrant"] == quadrant # УСЛОВИЕ фильтрации
    ]
    return {
        "quadrant": quadrant,
        "count": len(filtered_tasks),
        "tasks": filtered_tasks
    }

@router.get("/search")
async def search_tasks(q: str = Query(..., min_length=2)) -> dict:
    q_lower = q.lower()

    results = [
        task for task in tasks_db
        if (q_lower in (task.get("title") or "").lower()) 
        or (q_lower in (task.get("description") or "").lower())
    ]

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Задачи, содержащие '{q}', не найдены."
        )

    return {
        "query": q,
        "count": len(results),
        "tasks": results
    }  

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_by_id(task_id: int) -> TaskResponse:
    for task in tasks_db:
            if task["id"] == task_id:
                return task  # нашли — возвращаем словарь
    raise HTTPException( 
        status_code=400,
        detail=f"Задача с id {task_id} не найдена"
    )


# Мы указываем, что эндпоинт будет возвращать данные,
# соответствующие схеме TaskResponse
@router.post("/", response_model=TaskResponse,
status_code=201)
async def create_task(task: TaskCreate) -> TaskResponse:
    # Определяем квадрант
    if task.is_important and task.is_urgent:
        quadrant = "Q1"
    elif task.is_important and not task.is_urgent:
        quadrant = "Q2"
    elif not task.is_important and task.is_urgent:
        quadrant = "Q3"
    else:
        quadrant = "Q4"
    new_id = max([t["id"] for t in tasks_db], default=0) + 1 # Генерируем новый ID

    new_task = {
        "id": new_id,
        "title": task.title,
        "description": task.description,
        "is_important": task.is_important,
        "is_urgent": task.is_urgent,
        "quadrant": quadrant,
        "completed": False,
        "created_at": datetime.now()
    }
    tasks_db.append(new_task) # "Сохраняем" в нашу "базу данных"

    # Возвращаем созданную задачу (FastAPI автоматически
    # преобразует dict в Pydantic-модель Task)
    return new_task

@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task_update: TaskUpdate) -> TaskResponse:
    # ШАГ 1: по аналогии с GET ищем задачу по ID
    task = next((
        task for task in tasks_db
        if task["id"] == task_id),
        None
    )
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    # ШАГ 2: Получаем и обновляем только переданные поля (exclude_unset=True)
    # Без exclude_unset=True все None поля тоже попадут в словарь
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        task[field] = value
    # ШАГ 3: Пересчитываем квадрант, если изменились важность или срочность
    if "is_important" in update_data or "is_urgent" in update_data:
        if task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q1"
        elif task["is_important"] and not task["is_urgent"]:
            task["quadrant"] = "Q2"
        elif not task["is_important"] and task["is_urgent"]:
            task["quadrant"] = "Q3"
        else:
            task["quadrant"] = "Q4"
    return task


router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(task_id: int) -> TaskResponse:
    task = next((
        task for task in tasks_db
        if task["id"] == task_id),
        None
    )
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    task["completed"] = True
    task["completed_at"] = datetime.now()
    return

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int):
    task = next((
        task for task in tasks_db
        if task["id"] == task_id),
        None
    )
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    tasks_db.remove(task)

    return Response(status_code=204)
