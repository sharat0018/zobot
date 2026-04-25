import httpx
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class OllamaService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = "llama3.2:1b"
        
        self.system_prompt = """You are Zobot, an AI wealth advisor for Indian retail banking.

CRITICAL RULES:
1. ONLY use data explicitly provided in the prompt
2. NEVER make up product names, prices, or returns
3. If no data is provided, give a brief helpful answer based on general Indian finance knowledge
4. Quote exact numbers from the provided data when available
5. Respond in the user's selected language
6. NEVER refuse to answer financial questions — always be helpful

Your role:
- Explain financial data in simple terms
- Answer what the user asked using provided context
- Be concise (under 100 words)
- Be warm, helpful, and actionable

What you CANNOT do:
- Make up specific stock prices or fund returns
- Promise guaranteed returns
- Provide data not in the context when real data is available

Always be factual, concise, and customer-focused."""
    
    async def generate_response(self, user_message: str, context: Optional[Dict] = None) -> str:
        """Generate response using Ollama"""
        try:
            # Build context-aware prompt
            prompt = self._build_prompt(user_message, context)
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "system": self.system_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.4,
                            "num_predict": 200
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get('response', '')
                else:
                    return self._fallback_response(user_message, context)
        
        except Exception as e:
            print(f"Ollama Error: {e}")
            return self._fallback_response(user_message, context)
    
    def _build_prompt(self, user_message: str, context: Optional[Dict]) -> str:
        """Build context-aware prompt based on intent"""
        prompt = ""
        
        if context:
            # Add language instruction at the very top
            if 'language' in context:
                lang_map = {
                    "english": "CRITICAL: You MUST respond ONLY in English language. Do NOT use any other language.",
                    "hindi": "CRITICAL: You MUST respond ONLY in Hindi (Devanagari script). Use simple Hindi words.",
                    "tamil": "CRITICAL: You MUST respond ONLY in Tamil (Tamil script). Use simple Tamil words.",
                    "telugu": "CRITICAL: You MUST respond ONLY in Telugu (Telugu script). Use simple Telugu words.",
                    "marathi": "CRITICAL: You MUST respond ONLY in Marathi (Devanagari script). Use simple Marathi words.",
                    "bengali": "CRITICAL: You MUST respond ONLY in Bengali (Bengali script). Use simple Bengali words."
                }
                if context['language'] in lang_map:
                    prompt += f"{lang_map[context['language']]}\n\n"
        
        prompt += f"User Query: {user_message}\n\n"
        
        if context:
            intent = context.get('intent', 'general')
            
            # Provide ONLY relevant data based on intent
            if intent == "spending_analysis" and 'spending_data' in context:
                prompt += "=== SPENDING ANALYSIS DATA ===\n"
                spending = context['spending_data']
                prompt += f"Monthly Expenses: ₹{spending['monthly_expenses']:,.0f}\n"
                prompt += f"\nSpending Breakdown:\n"
                for category, amount in spending['spending_breakdown'].items():
                    if category != 'total':
                        prompt += f"- {category}: ₹{amount:,.0f}\n"
                if spending['savings_opportunities']:
                    prompt += "\nSavings Opportunities:\n"
                    for opp in spending['savings_opportunities']:
                        prompt += f"- {opp}\n"
                prompt += "\nYour task: Explain spending patterns and suggest improvements.\n"
            
            elif intent == "stock_query" and 'market_data' in context:
                prompt += "=== STOCK MARKET DATA ===\n"
                market = context['market_data']
                
                # Show specific stock first if user asked about it
                if market.get('specific_stocks'):
                    prompt += "CRITICAL: Use ONLY these exact numbers. DO NOT calculate or modify them.\n\n"
                    prompt += "Stock you asked about:\n"
                    for stock in market['specific_stocks']:
                        prompt += f"Company: {stock['symbol']}\n"
                        prompt += f"Current Price: ₹{stock['price']:,.2f}\n"
                        prompt += f"Change: {stock['change_percent']:+.2f}%\n"
                        prompt += f"Volume: {stock['volume']:,} shares\n"
                    prompt += "\nYour task: Explain if this stock is up or down today. Use EXACT numbers shown above. DO NOT calculate anything.\n"
                else:
                    # General market query
                    if 'market_indices' in market:
                        prompt += "Market Overview:\n"
                        for idx in market['market_indices']:
                            prompt += f"- {idx['name']}: ₹{idx['value']:,.2f} ({idx['change_percent']:+.2f}%)\n"
                    
                    if 'trending_stocks' in market:
                        prompt += "\nTop Trending Stocks:\n"
                        for stock in market['trending_stocks'][:5]:
                            prompt += f"- {stock['symbol']}: ₹{stock['price']:,.2f} ({stock['change_percent']:+.2f}%)\n"
                    
                    prompt += "\nYour task: Explain overall market performance using EXACT numbers above.\n"
            
            elif intent == "mutual_fund_query" and 'mutual_funds' in context:
                prompt += "=== MUTUAL FUNDS DATA ===\n"
                for fund in context['mutual_funds'][:5]:
                    prompt += f"- {fund['name']} ({fund['category']}): 1Y Return: {fund['returns_1y']}%, Min: ₹{fund['min_investment']:,}\n"
                prompt += "\nYour task: Explain mutual fund options based on user query.\n"
            
            elif intent == "investment_recommendation" and 'financial_profile' in context:
                prompt += "=== FINANCIAL PROFILE ===\n"
                profile = context['financial_profile']
                prompt += f"Monthly Income: ₹{profile['monthly_income']:,.0f}\n"
                prompt += f"Monthly Expenses: ₹{profile['monthly_expenses']:,.0f}\n"
                prompt += f"Savings Rate: {profile['savings_rate']}%\n"
                prompt += f"Stress Score: {profile['stress_score']}/100\n"
                prompt += f"Emergency Fund: {profile['emergency_status']}\n"
                if 'recommendations' in context:
                    prompt += "\nRecommended Products (from backend engine):\n"
                    for rec in context['recommendations']:
                        prompt += f"- {rec['product_name']} ({rec['product_type']}): Suitability {rec['suitability_score']:.1f}/100, Min ₹{rec['min_investment']:,}\n"
                prompt += "\nYour task: Explain these recommendations based on user's profile. DO NOT suggest any products not in the list above.\n"
            
            elif intent == "emergency_fund" and 'emergency_data' in context:
                prompt += "=== EMERGENCY FUND STATUS ===\n"
                emergency = context['emergency_data']
                prompt += f"Current Balance: ₹{emergency.get('liquid_balance', 0):,.0f}\n"
                prompt += f"Required (3-6 months): ₹{emergency.get('required_min', 0):,.0f} - ₹{emergency.get('required_max', 0):,.0f}\n"
                status = emergency.get('emergency_status', {})
                prompt += f"Status: {status.get('status', 'Unknown')}\n"
                prompt += "\nYour task: Explain emergency fund importance and current status.\n"
            
            elif intent == "financial_health" and 'stress_data' in context:
                prompt += "=== FINANCIAL STRESS SCORE ===\n"
                stress = context['stress_data']
                prompt += f"Overall Score: {stress['score']}/100\n"
                prompt += f"Risk Level: {stress['risk_level']}\n"
                prompt += f"Debt Ratio: {stress['factors']['debt_ratio']:.1f}%\n"
                prompt += f"Savings Rate: {stress['factors']['savings_rate']:.1f}%\n"
                prompt += "\nYour task: Explain financial health and suggest improvements.\n"
            
            else:
                prompt += "Your task: Answer the user's financial question helpfully using your knowledge of Indian personal finance, investments, and banking. Be concise and practical.\n"
        
        prompt += "\nIMPORTANT:\n"
        prompt += "- Answer ONLY what user asked\n"
        prompt += "- Use ONLY the data provided above\n"
        prompt += "- DO NOT make up product names, schemes, or numbers\n"
        prompt += "- DO NOT suggest anything not explicitly listed above\n"
        prompt += "- Keep response under 80 words\n"
        prompt += "- Be specific and actionable\n\n"
        prompt += "Your response:"
        
        return prompt

    
    def _fallback_response(self, user_message: str, context: Optional[Dict] = None) -> str:
        """Fallback response when Ollama is unavailable"""
        # If we have recommendations in context, show them
        if context and 'recommendations' in context:
            recs = context['recommendations']
            response = "Based on your financial profile, here are my top recommendations:\n\n"
            for i, rec in enumerate(recs[:3], 1):
                response += f"{i}. {rec['product_name']} - Suitability: {rec['suitability_score']:.1f}/100\n"
            return response
        
        if "invest" in user_message.lower():
            return "I can help you with investment recommendations. Let me analyze your financial profile first. Could you share your monthly income and expenses?"
        elif "emergency" in user_message.lower():
            return "Emergency fund is crucial before investing. Ideally, you should have 6 months of expenses saved in a liquid fund or savings account."
        elif "tax" in user_message.lower():
            return "For tax savings, ELSS (Equity Linked Savings Scheme) offers benefits under Section 80C with potential for higher returns. Would you like to know more?"
        else:
            return "I'm here to help you with your financial planning. What would you like to know about investments, savings, or financial planning?"
    
    async def detect_language(self, text: str) -> str:
        """Detect language of user input"""
        # Simple language detection (can be enhanced)
        hindi_chars = any('\u0900' <= char <= '\u097F' for char in text)
        tamil_chars = any('\u0B80' <= char <= '\u0BFF' for char in text)
        telugu_chars = any('\u0C00' <= char <= '\u0C7F' for char in text)
        
        if hindi_chars:
            return "hindi"
        elif tamil_chars:
            return "tamil"
        elif telugu_chars:
            return "telugu"
        else:
            return "english"
    
    async def translate_response(self, response: str, target_language: str) -> str:
        """Translate response to target language"""
        if target_language == "english":
            return response
        
        # Use Ollama for translation
        try:
            prompt = f"Translate the following to {target_language}:\n\n{response}"
            async with httpx.AsyncClient(timeout=30.0) as client:
                result = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                
                if result.status_code == 200:
                    return result.json().get('response', response)
        except:
            pass
        
        return response
