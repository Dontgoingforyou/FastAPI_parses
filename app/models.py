from sqlalchemy.orm import Mapped, mapped_column  # способ аннотации полей модели в алхимии 2.0, замена Column
from sqlalchemy import Integer, String, Date, Float, DateTime
from app.base import Base
from datetime import datetime


class SpimexTradingResult(Base):
    """Модель для таблицы spimex_trading_results """
    __tablename__ = 'spimex_trading_results'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exchange_product_id: Mapped[str] = mapped_column(String, nullable=False)
    exchange_product_name: Mapped[str] = mapped_column(String, nullable=False)
    oil_id: Mapped[str] = mapped_column(String, nullable=False)
    delivery_basis_id: Mapped[str] = mapped_column(String, nullable=False)
    delivery_basis_name: Mapped[str] = mapped_column(String, nullable=False)
    delivery_type_id: Mapped[str] = mapped_column(String, nullable=False)
    volume: Mapped[float] = mapped_column(Float, nullable=True)
    total: Mapped[float] = mapped_column(Float, nullable=True)
    count: Mapped[int] = mapped_column(Integer, nullable=True)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[str] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
