import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta

class IncomeEngine:
    def __init__(self):
        self.min_months = 3
    
    def calculate_stability_score(self, monthly_incomes: List[float]) -> float:
        """Calculate income stability score (0-100, higher is more stable)"""
        if len(monthly_incomes) < self.min_months:
            return 0.0
        
        avg_income = np.mean(monthly_incomes)
        std_dev = np.std(monthly_incomes)
        
        if avg_income == 0:
            return 0.0
        
        coefficient_of_variation = std_dev / avg_income
        stability_score = max(0, 100 - (coefficient_of_variation * 100))
        
        return round(stability_score, 2)
    
    def detect_income_type(self, stability_score: float) -> str:
        """Classify income type based on stability"""
        if stability_score >= 80:
            return "FIXED_SALARY"
        elif stability_score >= 50:
            return "VARIABLE_INCOME"
        else:
            return "IRREGULAR_INCOME"
    
    def recommend_sip_strategy(self, stability_score: float, monthly_income: float) -> Dict:
        """Recommend SIP strategy based on income stability"""
        income_type = self.detect_income_type(stability_score)
        
        if income_type == "FIXED_SALARY":
            return {
                "strategy": "FIXED_SIP",
                "recommended_amount": round(monthly_income * 0.20, 2),
                "frequency": "MONTHLY",
                "description": "Fixed monthly SIP recommended for stable income"
            }
        elif income_type == "VARIABLE_INCOME":
            return {
                "strategy": "DYNAMIC_SIP",
                "recommended_percentage": 15,
                "frequency": "MONTHLY",
                "description": "Dynamic SIP (15% of monthly income) for variable income"
            }
        else:
            return {
                "strategy": "FLEXIBLE_SIP",
                "recommended_percentage": 10,
                "frequency": "QUARTERLY",
                "description": "Flexible quarterly SIP for irregular income"
            }
    
    def analyze(self, transactions: List[Dict]) -> Dict:
        """Analyze income from transactions"""
        income_transactions = [t for t in transactions if t['amount'] > 0 and t['category'] in ['SALARY', 'INCOME', 'CREDIT']]
        
        if not income_transactions:
            return {
                "monthly_income": 0,
                "stability_score": 0,
                "income_type": "NO_DATA",
                "recommendation": "Insufficient data"
            }
        
        monthly_incomes = []
        for t in income_transactions:
            monthly_incomes.append(t['amount'])
        
        avg_income = np.mean(monthly_incomes)
        stability_score = self.calculate_stability_score(monthly_incomes)
        income_type = self.detect_income_type(stability_score)
        sip_strategy = self.recommend_sip_strategy(stability_score, avg_income)
        
        return {
            "monthly_income": round(avg_income, 2),
            "stability_score": stability_score,
            "income_type": income_type,
            "sip_strategy": sip_strategy
        }
