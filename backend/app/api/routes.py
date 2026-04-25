from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db, User, Transaction, Investment, ConsentLog
from app.models import (
    UserCreate, UserResponse, TransactionInput, 
    ChatMessage, ChatResponse, ProductRecommendation
)
from app.engines.income_engine import IncomeEngine
from app.engines.stress_score import StressScoreEngine
from app.engines.emergency_radar import EmergencyRadar
from app.engines.spend_analyzer import SpendAnalyzer
from app.services.recommendation import RecommendationEngine
from app.services.ollama_service import OllamaService
from app.services.indian_stock_api import GrowwAPIService
from app.security import validate_user_prompt, get_firewall_stats

router = APIRouter()

income_engine = IncomeEngine()
stress_engine = StressScoreEngine()
emergency_radar = EmergencyRadar()
spend_analyzer = SpendAnalyzer()
recommendation_engine = RecommendationEngine()
ollama_service = OllamaService()
indian_stock_service = GrowwAPIService()

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create new user"""
    db_user = User(email=user.email, name=user.name, phone=user.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/transactions/{user_id}")
def add_transactions(user_id: int, transactions: List[TransactionInput], db: Session = Depends(get_db)):
    """Add transactions for user"""
    for txn in transactions:
        db_txn = Transaction(
            user_id=user_id,
            amount=txn.amount,
            category=txn.category,
            description=txn.description,
            date=txn.date,
            merchant=txn.merchant
        )
        db.add(db_txn)
    db.commit()
    return {"message": f"Added {len(transactions)} transactions"}

@router.get("/analysis/income/{user_id}")
def analyze_income(user_id: int, db: Session = Depends(get_db)):
    """Analyze income variability"""
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    txn_data = [{"amount": t.amount, "category": t.category} for t in transactions]
    
    analysis = income_engine.analyze(txn_data)
    return analysis

@router.get("/analysis/stress/{user_id}")
def analyze_stress(user_id: int, db: Session = Depends(get_db)):
    """Calculate financial stress score"""
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    
    # Calculate user data
    income_txns = [t for t in transactions if t.amount > 0]
    expense_txns = [t for t in transactions if t.amount < 0]
    
    monthly_income = sum(t.amount for t in income_txns) / max(len(income_txns), 1)
    monthly_expenses = abs(sum(t.amount for t in expense_txns)) / max(len(expense_txns), 1)
    monthly_savings = monthly_income - monthly_expenses
    
    user_data = {
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "monthly_savings": monthly_savings,
        "monthly_debt": 0,
        "liquid_balance": 50000,
        "monthly_expenses_history": [monthly_expenses],
        "investments": []
    }
    
    stress_analysis = stress_engine.analyze(user_data)
    return stress_analysis

@router.get("/analysis/emergency/{user_id}")
def analyze_emergency(user_id: int, db: Session = Depends(get_db)):
    """Check emergency fund status"""
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    
    expense_txns = [t for t in transactions if t.amount < 0]
    monthly_expenses = abs(sum(t.amount for t in expense_txns)) / max(len(expense_txns), 1)
    
    user_data = {
        "liquid_balance": 50000,
        "monthly_expenses": monthly_expenses
    }
    
    emergency_analysis = emergency_radar.analyze(user_data)
    return emergency_analysis

@router.get("/analysis/spending/{user_id}")
def analyze_spending(user_id: int, db: Session = Depends(get_db)):
    """Analyze spending patterns"""
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    txn_data = [
        {
            "amount": t.amount,
            "description": t.description,
            "merchant": t.merchant or ""
        }
        for t in transactions
    ]
    
    spending_analysis = spend_analyzer.analyze_spending(txn_data)
    opportunities = spend_analyzer.detect_savings_opportunities(spending_analysis)
    
    return {
        "spending_analysis": spending_analysis,
        "savings_opportunities": opportunities
    }

@router.get("/recommendations/{user_id}", response_model=List[ProductRecommendation])
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    """Get personalized product recommendations"""
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    
    # Build user profile
    income_txns = [t for t in transactions if t.amount > 0]
    expense_txns = [t for t in transactions if t.amount < 0]
    
    monthly_income = sum(t.amount for t in income_txns) / max(len(income_txns), 1)
    monthly_expenses = abs(sum(t.amount for t in expense_txns)) / max(len(expense_txns), 1)
    
    user_profile = {
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        "liquid_balance": 50000,
        "stress_score": 65,
        "tax_saving_needed": True
    }
    
    recommendations = recommendation_engine.get_recommendations(user_profile)
    return recommendations

@router.get("/languages")
def get_supported_languages():
    """Get list of supported languages"""
    return {
        "languages": [
            {"code": "english", "name": "English", "native_name": "English"},
            {"code": "hindi", "name": "Hindi", "native_name": "हिन्दी"},
            {"code": "tamil", "name": "Tamil", "native_name": "தமிழ்"},
            {"code": "telugu", "name": "Telugu", "native_name": "తెలుగు"},
            {"code": "marathi", "name": "Marathi", "native_name": "मराठी"},
            {"code": "bengali", "name": "Bengali", "native_name": "বাংলা"}
        ]
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage, db: Session = Depends(get_db)):
    """Chat with Zobot AI - Supports Hindi, Tamil, Telugu, Marathi, Bengali"""
    
    # SECURITY LAYER: Validate prompt through firewall
    is_safe, sanitized_prompt, threat_type = validate_user_prompt(message.message, message.user_id)
    
    if not is_safe:
        return ChatResponse(
            response=f"⚠️ Security Alert: Your request was blocked due to potential {threat_type} attack. Please rephrase your query.",
            recommendations=None
        )
    
    # Use sanitized prompt for processing
    user_query = sanitized_prompt.lower()
    
    # Use user-selected language or auto-detect
    language = message.language if message.language else "english"
    
    # Auto-detect if not specified
    if language == "english" and any(char in message.message for char in ['ह', 'न', 'क', 'म', 'த', 'ன', 'త', 'న', 'ব', 'ন']):
        if any(char in message.message for char in ['ह', 'न', 'क', 'म']):
            language = "hindi"
        elif any(char in message.message for char in ['த', 'ன', 'க', 'ம']):
            language = "tamil"
        elif any(char in message.message for char in ['త', 'న', 'క', 'మ']):
            language = "telugu"
        elif any(char in message.message for char in ['ব', 'ন', 'ক', 'ম']):
            language = "bengali"
    
    # Classify user intent
    # Named companies — only these trigger stock_query
    KNOWN_STOCKS = ["reliance", "tcs", "hdfc", "infy", "infosys", "icici", "bharti", "airtel",
                    "itc", "wipro", "sbin", "lt", "ongc", "ntpc", "adani", "tatamotors",
                    "tata", "bajaj", "kotak", "axis", "hul", "hindustan", "maruti", "sunpharma",
                    "powergrid", "coalindia", "irctc", "zomato", "paytm", "nykaa"]

    intent = "general"
    if any(word in user_query for word in ["spend", "expense", "spending", "spent", "budget", "bills", "breakdown"]):
        intent = "spending_analysis"
    elif any(word in user_query for word in ["nifty", "sensex", "market index", "indices"]):
        intent = "stock_query"
    elif any(word in user_query for word in ["mutual fund", "mf", "sip", "elss", "fund"]):
        intent = "mutual_fund_query"
    elif any(stock in user_query for stock in KNOWN_STOCKS):
        # Only stock_query if a specific company is mentioned
        intent = "stock_query"
    elif any(word in user_query for word in ["invest", "investment", "portfolio", "recommend", "suggest",
                                              "where to invest", "how to invest", "stock", "share", "equity"]):
        intent = "investment_recommendation"
    elif any(word in user_query for word in ["emergency", "savings", "save"]):
        intent = "emergency_fund"
    elif any(word in user_query for word in ["stress", "financial health", "score"]):
        intent = "financial_health"
    
    # Get user context from database
    transactions = db.query(Transaction).filter(Transaction.user_id == message.user_id).all()
    
    # Calculate user financial context
    income_txns = [t for t in transactions if t.amount > 0]
    expense_txns = [t for t in transactions if t.amount < 0]
    
    monthly_income = sum(t.amount for t in income_txns) / max(len(income_txns), 1) if income_txns else 0
    monthly_expenses = abs(sum(t.amount for t in expense_txns)) / max(len(expense_txns), 1) if expense_txns else 0
    monthly_savings = monthly_income - monthly_expenses
    savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
    
    # Build context based on intent
    context = {
        "user_id": message.user_id,
        "language": language,
        "intent": intent
    }
    
    # Add relevant data based on intent only
    if intent == "spending_analysis":
        # Only spending data
        txn_data = [
            {"amount": t.amount, "description": t.description, "merchant": t.merchant or ""}
            for t in transactions
        ]
        spending_analysis = spend_analyzer.analyze_spending(txn_data)
        opportunities = spend_analyzer.detect_savings_opportunities(spending_analysis)
        
        context["spending_data"] = {
            "monthly_expenses": monthly_expenses,
            "spending_breakdown": spending_analysis,
            "savings_opportunities": opportunities
        }
    
    elif intent == "stock_query":
        try:
            stop_words = ['tell', 'me', 'about', 'show', 'stock', 'stocks', 'price', 'share', 'shares', 'the', 'this', 'that', 'how', 'is', 'doing', 'performance', 'trends', 'in']
            words = [w for w in user_query.lower().split() if w not in stop_words]
            search_query = ' '.join(words) if words else ''
            
            print(f"🔍 Stock query detected. Search term: '{search_query}'")
            
            specific_stocks = []
            if search_query:
                symbol = await indian_stock_service.search_stock_symbol(search_query)
                print(f"📊 Symbol found: {symbol}")
                
                if symbol:
                    stock_data = await indian_stock_service.get_stock_quote(symbol)
                    print(f"💹 Stock data: {stock_data}")
                    if stock_data:
                        specific_stocks.append(stock_data)
            
            trending = await indian_stock_service.get_trending_stocks()
            indices = await indian_stock_service.get_market_indices()
            
            print(f"✅ Market data ready: {len(specific_stocks)} specific, {len(trending)} trending, {len(indices)} indices")
            
            context["market_data"] = {
                "specific_stocks": specific_stocks if specific_stocks else None,
                "trending_stocks": trending[:10],
                "market_indices": indices
            }
        except Exception as e:
            print(f"❌ Market data error: {e}")
            import traceback
            traceback.print_exc()
    
    elif intent == "mutual_fund_query":
        # Only mutual fund data
        try:
            mutual_funds = await indian_stock_service.get_mutual_funds()
            context["mutual_funds"] = mutual_funds
        except Exception as e:
            print(f"MF data error: {e}")
    
    elif intent == "investment_recommendation":
        # Financial profile + recommendations
        user_data = {
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "monthly_savings": monthly_savings,
            "monthly_debt": 0,
            "liquid_balance": 50000,
            "monthly_expenses_history": [monthly_expenses],
            "investments": []
        }
        stress_analysis = stress_engine.analyze(user_data)
        emergency_analysis = emergency_radar.analyze(user_data)
        
        context["financial_profile"] = {
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "savings_rate": round(savings_rate, 1),
            "stress_score": stress_analysis['score'],
            "emergency_status": "adequate" if emergency_analysis['emergency_status']['adequate'] else "inadequate"
        }
        
        user_profile = {
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "liquid_balance": 50000,
            "stress_score": stress_analysis['score'],
            "tax_saving_needed": True
        }
        recommendations = recommendation_engine.get_recommendations(user_profile)
        context["recommendations"] = [
            {
                "product_name": r["product_name"] if isinstance(r, dict) else r.product_name,
                "product_type": r["product_type"] if isinstance(r, dict) else r.product_type,
                "suitability_score": r["suitability_score"] if isinstance(r, dict) else r.suitability_score,
                "risk_level": r["risk_level"] if isinstance(r, dict) else r.risk_level,
                "min_investment": r["min_investment"] if isinstance(r, dict) else r.min_investment
            } for r in recommendations[:3]
        ]
    
    elif intent == "emergency_fund":
        # Only emergency fund data
        user_data = {
            "liquid_balance": 50000,
            "monthly_expenses": monthly_expenses
        }
        emergency_analysis = emergency_radar.analyze(user_data)
        context["emergency_data"] = emergency_analysis
    
    elif intent == "financial_health":
        # Only stress score data
        user_data = {
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "monthly_savings": monthly_savings,
            "monthly_debt": 0,
            "liquid_balance": 50000,
            "monthly_expenses_history": [monthly_expenses],
            "investments": []
        }
        stress_analysis = stress_engine.analyze(user_data)
        context["stress_data"] = stress_analysis
    
    # Get AI response with focused context
    response = await ollama_service.generate_response(sanitized_prompt, context)
    
    # Return recommendations only for investment intent
    recommendations = None
    if intent == "investment_recommendation":
        try:
            user_profile = {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "liquid_balance": 50000,
                "stress_score": context.get("financial_profile", {}).get("stress_score", 65),
                "tax_saving_needed": True
            }
            recommendations = recommendation_engine.get_recommendations(user_profile)
        except Exception as e:
            print(f"Recommendation error: {e}")
    
    return ChatResponse(
        response=response,
        recommendations=recommendations
    )

@router.get("/market/mutual-funds")
async def get_mutual_funds(category: str = None):
    """Get mutual fund data from Indian Stock API"""
    funds = await indian_stock_service.get_mutual_funds(category)
    return {"data": funds}

@router.get("/market/indices")
async def get_market_indices():
    """Get market indices"""
    indices = await indian_stock_service.get_market_indices()
    return {"data": indices}

@router.get("/market/trending")
async def get_trending_stocks():
    """Get trending stocks"""
    trending = await indian_stock_service.get_trending_stocks()
    return {"data": trending}

@router.get("/market/nse-active")
async def get_nse_active():
    """Get NSE most active stocks"""
    active = await indian_stock_service.get_nse_most_active()
    return {"data": active}

@router.post("/investments/{user_id}")
def create_investment(user_id: int, product_name: str, amount: float, product_type: str = "MUTUAL_FUND", db: Session = Depends(get_db)):
    """Create investment order and forward to bank for processing"""
    # Validate user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check emergency fund
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    expense_txns = [t for t in transactions if t.amount < 0]
    monthly_expenses = abs(sum(t.amount for t in expense_txns)) / max(len(expense_txns), 1)
    
    user_data = {"liquid_balance": 50000, "monthly_expenses": monthly_expenses}
    emergency_analysis = emergency_radar.analyze(user_data)
    
    if not emergency_analysis['emergency_status']['adequate'] and product_type in ["EQUITY", "MUTUAL_FUND"]:
        raise HTTPException(
            status_code=400, 
            detail="Investment blocked: Build emergency fund (3-6 months expenses) before investing in market-linked products"
        )
    
    # Log consent
    consent = ConsentLog(
        user_id=user_id,
        consent_type="INVESTMENT",
        consent_given=True,
        consent_metadata={"product": product_name, "amount": amount, "product_type": product_type}
    )
    db.add(consent)
    
    # Create investment order
    investment = Investment(
        user_id=user_id,
        product_type=product_type,
        product_name=product_name,
        amount=amount,
        status="PENDING_BANK_APPROVAL"
    )
    db.add(investment)
    db.commit()
    db.refresh(investment)
    
    # Simulate bank API request
    bank_request = {
        "order_id": f"ZOBOT-{investment.id}",
        "user_id": user_id,
        "user_name": user.name,
        "user_email": user.email,
        "product_type": product_type,
        "product_name": product_name,
        "amount": amount,
        "payment_method": "UPI",
        "bank_account": "XXXX1234",
        "timestamp": datetime.now().isoformat()
    }
    
    return {
        "message": "Investment order created and forwarded to bank",
        "order_id": f"ZOBOT-{investment.id}",
        "status": "PENDING_BANK_APPROVAL",
        "bank_request": bank_request,
        "next_steps": [
            "Bank will verify account balance",
            "Payment gateway will process UPI/Net Banking",
            "Fund house will allocate units",
            "Confirmation will be sent via email/SMS"
        ],
        "estimated_processing_time": "2-3 business days"
    }

@router.get("/investments/{user_id}")
def get_investments(user_id: int, db: Session = Depends(get_db)):
    """Get user's investment orders"""
    investments = db.query(Investment).filter(Investment.user_id == user_id).all()
    return {
        "investments": [
            {
                "id": inv.id,
                "order_id": f"ZOBOT-{inv.id}",
                "product_type": inv.product_type,
                "product_name": inv.product_name,
                "amount": inv.amount,
                "status": inv.status,
                "created_at": inv.created_at.isoformat() if inv.created_at else None
            }
            for inv in investments
        ]
    }

@router.post("/investments/order/{investment_id}/simulate-bank")
def simulate_bank_response(investment_id: int, approved: bool = True, db: Session = Depends(get_db)):
    """Simulate bank approval/rejection (for demo purposes)"""
    investment = db.query(Investment).filter(Investment.id == investment_id).first()
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    if approved:
        investment.status = "COMPLETED"
        message = "Bank approved the investment. Units allocated successfully."
    else:
        investment.status = "REJECTED"
        message = "Bank rejected the investment due to insufficient funds."
    
    db.commit()
    
    return {
        "order_id": f"ZOBOT-{investment.id}",
        "status": investment.status,
        "message": message
    }

@router.get("/security/firewall-stats")
def get_security_stats():
    """Get prompt injection firewall statistics"""
    return get_firewall_stats()
