from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/Zobot.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    amount = Column(Float)
    category = Column(String)
    description = Column(String)
    date = Column(DateTime)
    merchant = Column(String)

class IncomeStats(Base):
    __tablename__ = "income_stats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    monthly_income = Column(Float)
    stability_score = Column(Float)
    income_type = Column(String)
    calculated_at = Column(DateTime, default=datetime.utcnow)

class StressScore(Base):
    __tablename__ = "stress_scores"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    score = Column(Float)
    debt_ratio = Column(Float)
    emergency_adequacy = Column(Float)
    savings_rate = Column(Float)
    spending_volatility = Column(Float)
    portfolio_diversification = Column(Float)
    calculated_at = Column(DateTime, default=datetime.utcnow)

class Investment(Base):
    __tablename__ = "investments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    product_type = Column(String)
    product_name = Column(String)
    amount = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ConsentLog(Base):
    __tablename__ = "consent_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    consent_type = Column(String)
    consent_given = Column(Boolean)
    consent_metadata = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
