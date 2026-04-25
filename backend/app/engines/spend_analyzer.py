from typing import Dict, List
from collections import defaultdict
import re

class SpendAnalyzer:
    def __init__(self):
        self.categories = {
            "FOOD": ["swiggy", "zomato", "restaurant", "cafe", "food", "dominos", "mcdonald"],
            "TRANSPORT": ["uber", "ola", "rapido", "petrol", "fuel", "metro", "bus"],
            "SHOPPING": ["amazon", "flipkart", "myntra", "ajio", "mall", "store"],
            "ENTERTAINMENT": ["netflix", "prime", "hotstar", "spotify", "movie", "theatre"],
            "UTILITIES": ["electricity", "water", "gas", "internet", "mobile", "recharge"],
            "HEALTHCARE": ["hospital", "pharmacy", "doctor", "medical", "clinic"],
            "EDUCATION": ["course", "book", "tuition", "school", "college"],
            "INVESTMENT": ["mutual fund", "sip", "stock", "equity", "fd"],
            "SALARY": ["salary", "income", "credit"],
            "EMI": ["emi", "loan", "credit card"]
        }
    
    def categorize_transaction(self, description: str, merchant: str = "") -> str:
        """Categorize transaction based on description and merchant"""
        text = f"{description} {merchant}".lower()
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        
        return "OTHER"
    
    def analyze_spending(self, transactions: List[Dict]) -> Dict:
        """Analyze spending patterns"""
        category_totals = defaultdict(float)
        total_expense = 0
        total_income = 0
        
        for txn in transactions:
            amount = abs(txn['amount'])
            category = self.categorize_transaction(
                txn.get('description', ''),
                txn.get('merchant', '')
            )
            
            if txn['amount'] < 0:
                category_totals[category] += amount
                total_expense += amount
            else:
                total_income += amount
        
        monthly_savings = total_income - total_expense
        savings_rate = (monthly_savings / total_income * 100) if total_income > 0 else 0
        
        return {
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "monthly_savings": round(monthly_savings, 2),
            "savings_rate": round(savings_rate, 2),
            "category_breakdown": dict(category_totals),
            "top_categories": sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def detect_savings_opportunities(self, spending_analysis: Dict) -> List[Dict]:
        """Detect areas where user can save money"""
        opportunities = []
        category_breakdown = spending_analysis['category_breakdown']
        total_expense = spending_analysis['total_expense']
        
        if total_expense == 0:
            return opportunities
        
        # Check food spending
        food_spending = category_breakdown.get('FOOD', 0)
        if food_spending / total_expense > 0.25:
            opportunities.append({
                "category": "FOOD",
                "current_spending": food_spending,
                "recommendation": "Food spending is high (>25%). Consider cooking at home more often.",
                "potential_savings": round(food_spending * 0.3, 2)
            })
        
        # Check entertainment
        entertainment_spending = category_breakdown.get('ENTERTAINMENT', 0)
        if entertainment_spending / total_expense > 0.15:
            opportunities.append({
                "category": "ENTERTAINMENT",
                "current_spending": entertainment_spending,
                "recommendation": "Entertainment spending is high. Review subscriptions.",
                "potential_savings": round(entertainment_spending * 0.2, 2)
            })
        
        # Check transport
        transport_spending = category_breakdown.get('TRANSPORT', 0)
        if transport_spending / total_expense > 0.20:
            opportunities.append({
                "category": "TRANSPORT",
                "current_spending": transport_spending,
                "recommendation": "Transport costs are high. Consider carpooling or public transport.",
                "potential_savings": round(transport_spending * 0.25, 2)
            })
        
        return opportunities
    
    def calculate_disposable_income(self, transactions: List[Dict]) -> float:
        """Calculate disposable income after essential expenses"""
        spending = self.analyze_spending(transactions)
        essential_categories = ['UTILITIES', 'HEALTHCARE', 'EMI', 'EDUCATION']
        
        essential_expense = sum(
            spending['category_breakdown'].get(cat, 0) 
            for cat in essential_categories
        )
        
        disposable = spending['total_income'] - essential_expense
        return round(disposable, 2)
