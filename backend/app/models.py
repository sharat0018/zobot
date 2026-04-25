from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    phone: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    phone: str
    
    class Config:
        from_attributes = True

class TransactionInput(BaseModel):
    amount: float
    category: str
    description: str
    date: datetime
    merchant: Optional[str] = None

class IncomeAnalysis(BaseModel):
    monthly_income: float
    stability_score: float
    income_type: str
    recommendation: str

class StressScoreResponse(BaseModel):
    score: float
    debt_ratio: float
    emergency_adequacy: float
    savings_rate: float
    spending_volatility: float
    portfolio_diversification: float
    risk_level: str

class ProductRecommendation(BaseModel):
    product_name: str
    product_type: str
    suitability_score: float
    expected_return: float
    risk_level: str
    min_investment: float
    tax_benefit: bool
    description: str

class ChatMessage(BaseModel):
    message: str
    user_id: int
    language: Optional[str] = "english"  # english, hindi, tamil, telugu, marathi, bengali

class ChatResponse(BaseModel):
    response: str
    recommendations: Optional[List[ProductRecommendation]] = None
    action_required: Optional[str] = None
