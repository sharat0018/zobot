from typing import Dict, List
import numpy as np

class StressScoreEngine:
    def __init__(self):
        self.weights = {
            "debt_ratio": 0.30,
            "emergency_adequacy": 0.20,
            "savings_rate": 0.20,
            "spending_volatility": 0.15,
            "portfolio_diversification": 0.15
        }
    
    def calculate_debt_ratio(self, monthly_debt: float, monthly_income: float) -> float:
        """Calculate debt-to-income ratio score (0-100, lower debt is better)"""
        if monthly_income == 0:
            return 0
        ratio = monthly_debt / monthly_income
        score = max(0, 100 - (ratio * 100))
        return round(score, 2)
    
    def calculate_emergency_adequacy(self, liquid_balance: float, monthly_expenses: float) -> float:
        """Calculate emergency fund adequacy (0-100)"""
        if monthly_expenses == 0:
            return 0
        months_covered = liquid_balance / monthly_expenses
        score = min(100, (months_covered / 6) * 100)
        return round(score, 2)
    
    def calculate_savings_rate(self, monthly_savings: float, monthly_income: float) -> float:
        """Calculate savings rate score (0-100)"""
        if monthly_income == 0:
            return 0
        rate = (monthly_savings / monthly_income) * 100
        score = min(100, rate * 5)
        return round(score, 2)
    
    def calculate_spending_volatility(self, monthly_expenses: List[float]) -> float:
        """Calculate spending volatility score (0-100, lower volatility is better)"""
        if len(monthly_expenses) < 2:
            return 50
        std_dev = np.std(monthly_expenses)
        avg_expense = np.mean(monthly_expenses)
        if avg_expense == 0:
            return 0
        cv = std_dev / avg_expense
        score = max(0, 100 - (cv * 100))
        return round(score, 2)
    
    def calculate_portfolio_diversification(self, investments: List[Dict]) -> float:
        """Calculate portfolio diversification score (0-100)"""
        if not investments:
            return 0
        
        asset_types = set([inv['product_type'] for inv in investments])
        diversification_score = min(100, len(asset_types) * 25)
        return round(diversification_score, 2)
    
    def calculate_composite_score(self, factors: Dict) -> float:
        """Calculate weighted composite stress score (0-100, higher is better)"""
        score = 0
        for factor, weight in self.weights.items():
            score += factors.get(factor, 0) * weight
        return round(score, 2)
    
    def get_risk_level(self, score: float) -> str:
        """Determine risk level based on stress score"""
        if score >= 75:
            return "LOW_STRESS"  # Aggressive allocation allowed
        elif score >= 50:
            return "MODERATE_STRESS"  # Balanced products
        else:
            return "HIGH_STRESS"  # Defensive products only
    
    def analyze(self, user_data: Dict) -> Dict:
        """Analyze financial stress"""
        factors = {
            "debt_ratio": self.calculate_debt_ratio(
                user_data.get('monthly_debt', 0),
                user_data.get('monthly_income', 1)
            ),
            "emergency_adequacy": self.calculate_emergency_adequacy(
                user_data.get('liquid_balance', 0),
                user_data.get('monthly_expenses', 1)
            ),
            "savings_rate": self.calculate_savings_rate(
                user_data.get('monthly_savings', 0),
                user_data.get('monthly_income', 1)
            ),
            "spending_volatility": self.calculate_spending_volatility(
                user_data.get('monthly_expenses_history', [1000])
            ),
            "portfolio_diversification": self.calculate_portfolio_diversification(
                user_data.get('investments', [])
            )
        }
        
        composite_score = self.calculate_composite_score(factors)
        risk_level = self.get_risk_level(composite_score)
        
        return {
            "score": composite_score,
            "risk_level": risk_level,
            **factors
        }
