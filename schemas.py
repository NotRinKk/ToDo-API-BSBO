from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from pydantic import computed_field

class TaskBase(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Название задачи")
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Описание задачи")
    is_important: bool = Field(
        ...,
        description="Важность задачи")
    deadline_at: Optional[date] = Field(
        None,
        description="Плановый срок выполнения задачи")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Новое название задачи")
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Новое описание")
    is_important: Optional[bool] = Field(
        None,
        description="Новая важность")
    deadline_at: Optional[date] = Field(
        None,
        description="Новый срок выполнения")
    completed: Optional[bool] = Field(
        None,
        description="Статус выполнения")

class TaskResponse(TaskBase):
    id: int = Field(
        ...,
        description="Уникальный идентификатор задачи",
        examples=[1])
    quadrant: str = Field(
        ...,
        description="Квадрант матрицы Эйзенхауэра (Q1, Q2, Q3, Q4)",
        examples=["Q1"])
    completed: bool = Field(
        default=False,
        description="Статус выполнения задачи")
    created_at: datetime = Field(
        ...,
        description="Дата и время создания задачи")
    completed_at: Optional[datetime] = Field(
        None,
        description="Дата и время завершения задачи")
    
    @computed_field
    @property
    def days_until_deadline(self) -> Optional[int]:
        """Вычисляемое поле: количество дней до дедлайна"""
        if not self.deadline_at:
            return None
        today = date.today()
        delta = self.deadline_at - today
        return delta.days
    
    @computed_field
    @property
    def is_urgent(self) -> bool:
        """Вычисляемое поле: срочность (True если до дедлайна <= 3 дня)"""
        if not self.deadline_at:
            return False
        days = self.days_until_deadline
        return days is not None and days <= 3

    class Config:
        from_attributes = True