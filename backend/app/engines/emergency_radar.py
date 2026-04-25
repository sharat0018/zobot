from typing import Dict, List

class EmergencyRadar:
    def __init__(self):
        self.min_emergency_months = 3
        self.recommended_emergency_months = 6
    
    def check_emergency_fund(self, liquid_balance: float, monthly_expenses: float) -> Dict:
        """Check if user has adequate emergency fund"""
        if monthly_expenses == 0:
            return {
                "adequate": False,
                "months_covered": 0,
                "shortfall": 0,
                "recommendation": "Unable to calculate - no expense data"
            }
        
        months_covered = liquid_balance / monthly_expenses
        min_required = monthly_expenses * self.min_emergency_months
        recommended_amount = monthly_expenses * self.recommended_emergency_months
        
        if months_covered >= self.min_emergency_months:
            return {
                "adequate": True,
                "months_covered": round(months_covered, 1),
                "shortfall": 0,
                "recommendation": "Emergency fund adequate. Safe to invest in equity."
            }
        else:
            shortfall = min_required - liquid_balance
            return {
                "adequate": False,
                "months_covered": round(months_covered, 1),
                "shortfall": round(shortfall, 2),
                "recommendation": f"Build emergency fund first. Need ₹{shortfall:,.0f} more."
            }
    
    def get_allowed_products(self, emergency_status: Dict) -> List[str]:
        """Return allowed product types based on emergency fund status"""
        if emergency_status['adequate']:
            return ["EQUITY", "MUTUAL_FUND", "ELSS", "FD", "LIQUID_FUND", "NPS"]
        else:
            return ["FD", "LIQUID_FUND", "SAVINGS"]
    
    def gate_recommendation(self, product_type: str, emergency_status: Dict) -> Dict:
        """Gate product recommendation based on emergency fund"""
        allowed_products = self.get_allowed_products(emergency_status)
        
        if product_type in allowed_products:
            return {
                "allowed": True,
                "reason": "Emergency fund adequate"
            }
        else:
            return {
                "allowed": False,
                "reason": f"Emergency fund inadequate. Only {', '.join(allowed_products)} allowed.",
                "alternative_products": allowed_products
            }
    
    def analyze(self, user_data: Dict) -> Dict:
        """Analyze emergency fund status and investment eligibility"""
        liquid_balance = user_data.get('liquid_balance', 0)
        monthly_expenses = user_data.get('monthly_expenses', 0)
        
        emergency_status = self.check_emergency_fund(liquid_balance, monthly_expenses)
        allowed_products = self.get_allowed_products(emergency_status)
        
        return {
            "emergency_status": emergency_status,
            "allowed_products": allowed_products,
            "can_invest_equity": emergency_status['adequate']
        }
