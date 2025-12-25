from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Field
from config import DB_URL

engine = create_async_engine(DB_URL, echo=False)
DBSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=AsyncSession)

class WeatherRecord(SQLModel, table=True):
    __tablename__ = "weather_records"

    id: int | None = Field(primary_key=True)
    date: str
    time_of_day: str
    temperature: str
    condition: str
    city: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

async def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        await db.close()
