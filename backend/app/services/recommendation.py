from typing import Dict, List
from app.engines.stress_score import StressScoreEngine
from app.engines.emergency_radar import EmergencyRadar

class RecommendationEngine:
    def __init__(self):
        self.stress_engine = StressScoreEngine()
        self.emergency_radar = EmergencyRadar()
        
        self.products = [
            {
                "id": "prod001",
                "name": "HDFC Equity Fund",
                "type": "MUTUAL_FUND",
                "category": "EQUITY",
                "min_investment": 500,
                "expected_return": 12.5,
                "risk": "HIGH",
                "tax_benefit": False,
                "revenue_yield": 0.018,
                "description": "Large-cap equity fund for long-term growth"
            },
            {
                "id": "prod002",
                "name": "ICICI Liquid Fund",
                "type": "LIQUID_FUND",
                "category": "LIQUID",
                "min_investment": 100,
                "expected_return": 6.8,
                "risk": "LOW",
                "tax_benefit": False,
                "revenue_yield": 0.005,
                "description": "Low-risk liquid fund for emergency corpus"
            },
            {
                "id": "prod003",
                "name": "SBI ELSS Tax Saver",
                "type": "ELSS",
                "category": "EQUITY",
                "min_investment": 500,
                "expected_return": 14.2,
                "risk": "MEDIUM",
                "tax_benefit": True,
                "revenue_yield": 0.015,
                "description": "Tax-saving equity fund with 3-year lock-in"
            },
            {
                "id": "prod004",
                "name": "Bank Fixed Deposit",
                "type": "FD",
                "category": "FIXED_INCOME",
                "min_investment": 1000,
                "expected_return": 7.5,
                "risk": "LOW",
                "tax_benefit": False,
                "revenue_yield": 0.008,
                "description": "Guaranteed returns with capital protection"
            },
            {
                "id": "prod005",
                "name": "NPS Tier 1",
                "type": "NPS",
                "category": "RETIREMENT",
                "min_investment": 500,
                "expected_return": 10.5,
                "risk": "MEDIUM",
                "tax_benefit": True,
                "revenue_yield": 0.012,
                "description": "Retirement savings with tax benefits"
            }
        ]
    
    def calculate_suitability_score(self, product: Dict, user_profile: Dict) -> float:
        """Calculate product suitability based on user profile"""
        score = 50
        
        # Risk alignment
        stress_score = user_profile.get('stress_score', 50)
        if product['risk'] == 'LOW':
            score += 20 if stress_score < 60 else 10
        elif product['risk'] == 'MEDIUM':
            score += 20 if 40 <= stress_score <= 80 else 5
        else:  # HIGH
            score += 20 if stress_score > 70 else -10
        
        # Income alignment
        monthly_income = user_profile.get('monthly_income', 0)
        if product['min_investment'] <= monthly_income * 0.1:
            score += 15
        
        return min(100, max(0, score))
    
    def calculate_stress_compatibility(self, product: Dict, stress_score: float) -> float:
        """Check if product is compatible with user's stress level
        
        Stress Score Ranges:
        - Below 50: Defensive products only (LOW risk)
        - 50-75: Balanced products (LOW, MEDIUM risk)
        - Above 75: Aggressive allocation allowed (all risk levels)
        """
        if stress_score >= 75:
            # Aggressive allocation allowed
            return 100
        elif stress_score >= 50:
            # Balanced products only
            return 100 if product['risk'] in ['LOW', 'MEDIUM'] else 20
        else:
            # Defensive products only
            return 100 if product['risk'] == 'LOW' else 10
    
    def calculate_tax_fit(self, product: Dict, user_profile: Dict) -> float:
        """Calculate tax benefit fit"""
        needs_tax_saving = user_profile.get('tax_saving_needed', False)
        if product['tax_benefit'] and needs_tax_saving:
            return 100
        elif product['tax_benefit']:
            return 70
        else:
            return 50
    
    def calculate_final_score(self, product: Dict, user_profile: Dict) -> float:
        """Calculate final ranking score"""
        suitability = self.calculate_suitability_score(product, user_profile)
        stress_compat = self.calculate_stress_compatibility(product, user_profile.get('stress_score', 50))
        tax_fit = self.calculate_tax_fit(product, user_profile)
        revenue_yield = product['revenue_yield'] * 1000
        strategic_boost = 10
        
        final_score = (
            0.4 * suitability +
            0.2 * stress_compat +
            0.15 * tax_fit +
            0.15 * revenue_yield +
            0.1 * strategic_boost
        )
        
        return round(final_score, 2)
    
    def get_recommendations(self, user_profile: Dict) -> List[Dict]:
        """Get ranked product recommendations"""
        # Check emergency fund status
        emergency_analysis = self.emergency_radar.analyze(user_profile)
        allowed_products = emergency_analysis['allowed_products']
        
        recommendations = []
        for product in self.products:
            # Filter by emergency fund eligibility
            if product['type'] not in allowed_products:
                continue
            
            final_score = self.calculate_final_score(product, user_profile)
            
            recommendations.append({
                "product_name": product['name'],
                "product_type": product['type'],
                "suitability_score": final_score,
                "expected_return": product['expected_return'],
                "risk_level": product['risk'],
                "min_investment": product['min_investment'],
                "tax_benefit": product['tax_benefit'],
                "description": product['description']
            })
        
        # Sort by suitability score
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return recommendations[:5]
