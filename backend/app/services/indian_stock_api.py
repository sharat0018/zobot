from typing import Dict, List, Optional
from dotenv import load_dotenv
from growwapi import GrowwAPI
from datetime import datetime, timedelta
import os

load_dotenv()

class GrowwAPIService:
    def __init__(self):
        self.api_token = os.getenv("GROWW_API_KEY")
        self.groww = GrowwAPI(self.api_token)
        self.instruments_cache = None
    
    async def search_stock_symbol(self, company_name: str) -> Optional[str]:
        """Search for stock symbol by company name"""
        # Try direct symbol lookup first
        try:
            search_term = company_name.upper().replace(' ', '')
            
            # Try as direct trading symbol
            result = self.groww.get_instrument_by_exchange_and_trading_symbol(
                exchange=self.groww.EXCHANGE_NSE,
                trading_symbol=search_term
            )
            if result:
                print(f"✓ Direct match: {search_term}")
                return search_term
        except:
            pass
        
        # If direct match fails, search in full instrument list
        try:
            if self.instruments_cache is None:
                print("Loading NSE instruments (one-time, ~10 sec)...")
                self.instruments_cache = self.groww.get_all_instruments()
                print(f"✓ Loaded {len(self.instruments_cache)} instruments")
            
            search_lower = company_name.lower().replace(' ', '')
            
            # Search in NSE CASH segment only
            for _, inst in self.instruments_cache.iterrows():
                if inst.get('exchange') != 'NSE' or inst.get('segment') != 'CASH':
                    continue
                    
                symbol = str(inst.get('trading_symbol', '')).lower()
                company = str(inst.get('company_name', '')).lower().replace(' ', '')
                
                if search_lower in symbol or search_lower in company:
                    found_symbol = inst.get('trading_symbol')
                    print(f"✓ Found: {inst.get('company_name')} -> {found_symbol}")
                    return found_symbol
            
            print(f"✗ No match for: {company_name}")
            return None
        except Exception as e:
            print(f"Search error: {e}")
            return None
    
    async def get_mutual_funds(self, category: Optional[str] = None) -> List[Dict]:
        """Fetch mutual fund data - Groww API doesn't provide MF data, using curated list"""
        funds = [
            {"id": "mf001", "name": "HDFC Equity Fund", "category": "EQUITY", "returns_1y": 12.5, "returns_3y": 15.2, "risk": "HIGH", "min_investment": 500, "expense_ratio": 1.8, "aum": "₹15,000 Cr"},
            {"id": "mf002", "name": "ICICI Liquid Fund", "category": "LIQUID", "returns_1y": 6.8, "returns_3y": 6.5, "risk": "LOW", "min_investment": 100, "expense_ratio": 0.5, "aum": "₹25,000 Cr"},
            {"id": "mf003", "name": "SBI ELSS Tax Saver", "category": "ELSS", "returns_1y": 14.2, "returns_3y": 16.8, "risk": "MEDIUM", "min_investment": 500, "expense_ratio": 1.5, "aum": "₹12,500 Cr"},
            {"id": "mf004", "name": "Axis Bluechip Fund", "category": "EQUITY", "returns_1y": 13.8, "returns_3y": 17.5, "risk": "HIGH", "min_investment": 500, "expense_ratio": 1.9, "aum": "₹18,000 Cr"},
            {"id": "mf005", "name": "Kotak Debt Hybrid", "category": "DEBT", "returns_1y": 8.5, "returns_3y": 9.2, "risk": "LOW", "min_investment": 1000, "expense_ratio": 1.2, "aum": "₹8,500 Cr"},
            {"id": "mf006", "name": "Parag Parikh Flexi Cap", "category": "EQUITY", "returns_1y": 15.2, "returns_3y": 19.8, "risk": "HIGH", "min_investment": 1000, "expense_ratio": 2.1, "aum": "₹22,000 Cr"},
            {"id": "mf007", "name": "UTI Nifty Index Fund", "category": "INDEX", "returns_1y": 11.5, "returns_3y": 14.2, "risk": "MEDIUM", "min_investment": 500, "expense_ratio": 0.8, "aum": "₹10,000 Cr"},
            {"id": "mf008", "name": "Mirae Asset Large Cap", "category": "EQUITY", "returns_1y": 13.2, "returns_3y": 16.5, "risk": "HIGH", "min_investment": 500, "expense_ratio": 1.7, "aum": "₹16,500 Cr"}
        ]
        
        if category:
            return [f for f in funds if f["category"] == category.upper()]
        return funds
    
    async def get_stock_quote(self, symbol: str) -> Dict:
        """Fetch stock quote from Groww API"""
        try:
            response = self.groww.get_quote(
                trading_symbol=symbol.upper(),
                exchange=self.groww.EXCHANGE_NSE,
                segment=self.groww.SEGMENT_CASH
            )
            
            return {
                "symbol": symbol.upper(),
                "name": symbol.upper(),
                "price": float(response.get('last_price', 0)),
                "change": float(response.get('day_change', 0)),
                "change_percent": float(response.get('day_change_perc', 0)),
                "volume": int(response.get('volume', 0))
            }
        except Exception as e:
            print(f"Groww API Error for {symbol}: {e}")
            return None
    
    async def get_market_indices(self) -> List[Dict]:
        """Fetch market indices using get_quote"""
        indices = []
        try:
            nifty = self.groww.get_quote(
                trading_symbol="NIFTY",
                exchange=self.groww.EXCHANGE_NSE,
                segment=self.groww.SEGMENT_CASH
            )
            indices.append({
                "name": "NIFTY 50",
                "value": float(nifty.get('last_price', 0)),
                "change": float(nifty.get('day_change', 0)),
                "change_percent": float(nifty.get('day_change_perc', 0))
            })
        except Exception as e:
            print(f"Error fetching NIFTY: {e}")
        
        return indices
    
    async def get_trending_stocks(self) -> List[Dict]:
        """Fetch trending stocks from Groww API"""
        stocks_to_fetch = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK", "BHARTIARTL", "ITC", "LT", "SBIN", "WIPRO"]
        
        trending = []
        for symbol in stocks_to_fetch:
            try:
                response = self.groww.get_quote(
                    trading_symbol=symbol,
                    exchange=self.groww.EXCHANGE_NSE,
                    segment=self.groww.SEGMENT_CASH
                )
                
                if response:
                    trending.append({
                        "name": symbol,
                        "symbol": symbol,
                        "price": float(response.get('last_price', 0)),
                        "change_percent": float(response.get('day_change_perc', 0)),
                        "volume": int(response.get('volume', 0))
                    })
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue
        
        return trending
    
    async def get_nse_most_active(self) -> List[Dict]:
        """Fetch NSE most active stocks"""
        return self.get_trending_stocks()
    
    async def get_historical_data(self, symbol: str, days: int = 30) -> List[Dict]:
        """Fetch historical candle data"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            response = self.groww.get_historical_candles(
                exchange=self.groww.EXCHANGE_NSE,
                segment=self.groww.SEGMENT_CASH,
                groww_symbol=f"NSE-{symbol}",
                start_time=start_time.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=end_time.strftime("%Y-%m-%d %H:%M:%S"),
                candle_interval=self.groww.CANDLE_INTERVAL_DAY_1
            )
            
            return response.get('data', [])
        except Exception as e:
            print(f"Groww API Error: {e}")
            raise
