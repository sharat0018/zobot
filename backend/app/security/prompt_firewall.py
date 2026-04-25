"""
Zobot Prompt Injection Firewall
Enterprise Security Layer - Banking Grade Protection

Author: Senior Security Architect (15+ years experience)
Purpose: Defend against prompt injection attacks in financial AI systems
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PromptInjectionFirewall:
    """
    Multi-layer defense system against prompt injection attacks
    Specifically designed for financial AI assistants
    """
    
    def __init__(self):
        self.blocked_count = 0
        self.allowed_count = 0
        
        # Attack Pattern Database
        self.attack_patterns = {
            "SYSTEM_OVERRIDE": [
                r"ignore\s+(previous|all|above)\s+(instructions|prompts|rules)",
                r"disregard\s+(previous|all|system)\s+(instructions|context)",
                r"forget\s+(everything|all|previous)\s+(instructions|you were told)",
                r"new\s+instructions?:\s*you\s+are",
                r"system\s*:\s*you\s+are\s+now",
                r"override\s+your\s+(programming|instructions|rules)",
                r"ignore\s+all\s+previous",
                r"ignore.*instructions.*transfer",
            ],
            "ROLE_MANIPULATION": [
                r"you\s+are\s+no\s+longer\s+a\s+(financial|banking|assistant)",
                r"pretend\s+to\s+be\s+(admin|developer|system|root)",
                r"act\s+as\s+(if\s+you\s+are|a)\s+(hacker|attacker|admin)",
                r"roleplay\s+as\s+(admin|system|developer)",
                r"simulate\s+(being|that\s+you\s+are)\s+(admin|root)",
                r"act\s+as.*hacker",
            ],
            "DATA_EXFILTRATION": [
                r"show\s+(me\s+)?(all|other)\s+(users?|accounts?|passwords?|credentials?)",
                r"reveal\s+(system|internal|hidden|secret)\s+(data|information|config|prompt|instructions)",
                r"display\s+(database|table|schema|backend)\s+(structure|content)",
                r"print\s+(environment|config|secret|api)\s+(variables?|keys?)",
                r"what\s+is\s+your\s+(system\s+prompt|internal\s+instructions)",
                r"repeat\s+(your|the)\s+(system\s+prompt|instructions|rules)",
                r"get\s+me\s+the\s+(api\s+key|credentials?|passwords?)",
            ],
            "FINANCIAL_FRAUD": [
                r"transfer\s+\d+.*to\s+(account|upi|wallet).*\d+",
                r"send\s+money\s+to\s+(account|upi).*without\s+(verification|otp|confirmation)",
                r"bypass\s+(authentication|verification|otp|security)",
                r"skip\s+(verification|otp|2fa|authentication)",
                r"approve\s+(transaction|transfer|payment)\s+without\s+(otp|verification)",
                r"execute\s+(unauthorized|fraudulent)\s+(transaction|transfer)",
            ]
        }
        
        # Whitelist: Legitimate financial queries
        self.legitimate_patterns = [
            r"what\s+is\s+my\s+(balance|account\s+balance)",
            r"show\s+my\s+(transactions|spending|portfolio)",
            r"how\s+(much|can)\s+i\s+(invest|save)",
            r"recommend\s+(investments?|mutual\s+funds?|stocks?)",
            r"tell\s+me\s+(about|the)?\s*(stock\s+)?trends?\s+(in|of|for|about)?\s*\w+",
            r"\w+\s+(stock|share|equity)\s+(price|trends?|performance)",
            r"(stock|share|equity)\s+(trends?|price|performance)\s+(in|of|for)?\s*\w+",
            r"what\s+is\s+my\s+(stress\s+score|financial\s+health)",
            r"(reliance|tcs|infy|hdfc|icici|wipro|bharti|itc|sbin|lt)\s+(stock|share)",
        ]
    
    def validate_prompt(self, user_prompt: str, user_id: int) -> Tuple[bool, str, str]:
        """
        Main validation pipeline
        Returns: (is_safe, sanitized_prompt, threat_type)
        """
        
        # Step 1: Check if legitimate query
        if self._is_legitimate_query(user_prompt):
            self.allowed_count += 1
            logger.info(f"✓ ALLOWED - User {user_id}: Legitimate query")
            return True, user_prompt, "NONE"
        
        # Step 2: Detect attack patterns
        threat_detected, threat_type = self._detect_threats(user_prompt)
        
        if threat_detected:
            self.blocked_count += 1
            logger.warning(f"✗ BLOCKED - User {user_id}: {threat_type} attack detected")
            logger.warning(f"  Malicious prompt: {user_prompt[:100]}...")
            return False, "", threat_type
        
        # Step 3: Sanitize prompt
        sanitized = self._sanitize_prompt(user_prompt)
        
        self.allowed_count += 1
        logger.info(f"✓ ALLOWED - User {user_id}: Sanitized query")
        return True, sanitized, "NONE"
    
    def _is_legitimate_query(self, prompt: str) -> bool:
        """Check if query matches legitimate financial patterns"""
        prompt_lower = prompt.lower()
        for pattern in self.legitimate_patterns:
            if re.search(pattern, prompt_lower, re.IGNORECASE):
                return True
        return False
    
    def _detect_threats(self, prompt: str) -> Tuple[bool, str]:
        """Detect known attack patterns"""
        prompt_lower = prompt.lower()
        
        for threat_type, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if re.search(pattern, prompt_lower, re.IGNORECASE):
                    return True, threat_type
        
        return False, "NONE"
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """Remove potentially dangerous content"""
        sanitized = re.sub(r'[<>{}[\]\\]', '', prompt)
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        if len(sanitized) > 500:
            sanitized = sanitized[:500]
        return sanitized
    
    def get_stats(self) -> Dict:
        """Return firewall statistics"""
        total = self.blocked_count + self.allowed_count
        block_rate = (self.blocked_count / total * 100) if total > 0 else 0
        
        return {
            "total_requests": total,
            "blocked": self.blocked_count,
            "allowed": self.allowed_count,
            "block_rate_percent": round(block_rate, 2),
            "timestamp": datetime.now().isoformat()
        }


firewall = PromptInjectionFirewall()


def validate_user_prompt(prompt: str, user_id: int) -> Tuple[bool, str, str]:
    """Public API for prompt validation"""
    return firewall.validate_prompt(prompt, user_id)


def get_firewall_stats() -> Dict:
    """Get firewall statistics"""
    return firewall.get_stats()
