from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional


class SpimexTradingResultBase(BaseModel):
    """ Базовая схема для работы с торговыми результатами """

    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str
    volume: Optional[float] = None
    total: Optional[float] = None
    count: Optional[int] = None
    date: date


class SpimexTradingResultResponse(SpimexTradingResultBase):
    """Схема для ответа API."""
    id: int

    class Config:
        from_attributes = True


class SpimexTradingResultQuery(BaseModel):
    """Схема запроса с валидацией дат"""

    start_date: str
    end_date: str


    @field_validator("start_date", "end_date")
    def validate_date_format(cls, value: str) -> date:
        """Валидация даты в формат DD-MM-YYYY """

        try:
            return datetime.strptime(value, "%d-%m-%Y").date()
        except ValueError:
            raise ValueError("Дата должна быть в формате DD-MM-YYYY")
