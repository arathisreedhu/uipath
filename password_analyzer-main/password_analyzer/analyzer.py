"""
Core password analysis using zxcvbn and custom algorithms.
"""

import logging
from typing import Dict, List, Optional, Any
from zxcvbn import zxcvbn
from .entropy import EntropyCalculator
from .pattern_detector import PatternDetector

logger = logging.getLogger(__name__)


class PasswordAnalyzer:
    """
    Analyzes password strength using multiple techniques.
    """
    
    def __init__(self):
        self.entropy_calc = EntropyCalculator()
        self.pattern_detector = PatternDetector()
    
    def analyze(
        self, 
        password: str, 
        user_inputs: Optional[List[str]] = None,
        use_entropy: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive password analysis.
        
        Args:
            password: The password to analyze
            user_inputs: Optional list of user-specific context (names, emails, etc.)
            use_entropy: Whether to calculate custom entropy metrics
            
        Returns:
            Dictionary containing all analysis results
        """
        if not password:
            return {
                'error': 'Password cannot be empty',
                'score': 0
            }
        
        # Basic zxcvbn analysis (limit password length to avoid errors)
        user_inputs = user_inputs or []
        # zxcvbn has a max length of 72 characters
        password_for_zxcvbn = password[:72] if len(password) > 72 else password
        zxcvbn_result = zxcvbn(password_for_zxcvbn, user_inputs=user_inputs)
        
        # Pattern detection
        patterns = self.pattern_detector.detect_patterns(password)
        
        # Check for contextual items
        contextual_matches = self._check_contextual_items(password, user_inputs)
        
        # Custom entropy calculation
        entropy_result = None
        if use_entropy:
            entropy_result = self.entropy_calc.calculate(password)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            zxcvbn_result,
            patterns,
            contextual_matches,
            entropy_result
        )
        
        # Compile results
        result = {
            'password_length': len(password),
            'zxcvbn_score': zxcvbn_result['score'],
            'zxcvbn_feedback': zxcvbn_result['feedback'],
            'guesses': zxcvbn_result['guesses'],
            'crack_times_display': zxcvbn_result['crack_times_display'],
            'patterns_detected': patterns,
            'contextual_matches': contextual_matches,
            'has_contextual_risk': len(contextual_matches) > 0,
            'entropy': entropy_result,
            'recommendations': recommendations,
            'overall_risk': self._calculate_risk_level(
                zxcvbn_result['score'],
                contextual_matches,
                patterns
            )
        }
        
        logger.info(f"Password analyzed: length={len(password)}, score={result['zxcvbn_score']}")
        
        return result
    
    def _check_contextual_items(self, password: str, user_inputs: List[str]) -> List[str]:
        """Check if password contains any user-provided contextual items."""
        matches = []
        password_lower = password.lower()
        
        for item in user_inputs:
            if item and len(item) >= 3:  # Only check meaningful items
                if item.lower() in password_lower:
                    matches.append(item)
        
        return matches
    
    def _generate_recommendations(
        self,
        zxcvbn_result: Dict,
        patterns: Dict,
        contextual_matches: List[str],
        entropy_result: Optional[Dict]
    ) -> List[str]:
        """Generate human-readable recommendations."""
        recommendations = []
        
        # Add zxcvbn warnings
        if zxcvbn_result['feedback']['warning']:
            recommendations.append(f"⚠️  {zxcvbn_result['feedback']['warning']}")
        
        # Add zxcvbn suggestions
        for suggestion in zxcvbn_result['feedback']['suggestions']:
            recommendations.append(f"💡 {suggestion}")
        
        # Contextual warnings
        if contextual_matches:
            recommendations.append(
                f"🚨 CRITICAL: Password contains personal information: {', '.join(contextual_matches)}. "
                "This makes it extremely vulnerable to targeted attacks!"
            )
        
        # Pattern-specific recommendations
        if patterns['repeated_sequences']:
            recommendations.append(
                "🔄 Avoid repeated character sequences (e.g., 'aaa', '123')"
            )
        
        if patterns['keyboard_patterns']:
            recommendations.append(
                "⌨️  Avoid keyboard patterns (e.g., 'qwerty', 'asdf')"
            )
        
        if patterns['dates']:
            recommendations.append(
                "📅 Avoid dates (birthdays, anniversaries) as they're easily guessable"
            )
        
        if patterns['leet_speak']:
            recommendations.append(
                "🔡 Simple letter-to-number substitutions (l33t sp34k) don't add much security"
            )
        
        # Entropy-based recommendations
        if entropy_result and entropy_result['entropy_bits'] < 50:
            recommendations.append(
                f"📊 Low entropy ({entropy_result['entropy_bits']:.1f} bits). "
                "Aim for at least 50-60 bits by increasing length and character variety"
            )
        
        # General best practices
        if not recommendations:
            recommendations.append("✅ Good password! Continue using unique passwords for each account")
        
        recommendations.append(
            "🎯 Best practice: Use a passphrase (4+ random words) or a password manager"
        )
        
        return recommendations
    
    def _calculate_risk_level(
        self,
        zxcvbn_score: int,
        contextual_matches: List[str],
        patterns: Dict
    ) -> str:
        """Calculate overall risk level."""
        if contextual_matches:
            return "CRITICAL"
        
        if zxcvbn_score == 0:
            return "VERY_HIGH"
        elif zxcvbn_score == 1:
            return "HIGH"
        elif zxcvbn_score == 2:
            return "MEDIUM"
        elif zxcvbn_score == 3:
            return "LOW"
        else:
            return "VERY_LOW"
    
    def batch_analyze(
        self,
        passwords: List[str],
        user_inputs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple passwords.
        
        Args:
            passwords: List of passwords to analyze
            user_inputs: Optional user context
            
        Returns:
            List of analysis results
        """
        results = []
        for pwd in passwords:
            result = self.analyze(pwd, user_inputs=user_inputs)
            results.append(result)
        
        logger.info(f"Batch analyzed {len(passwords)} passwords")
        return results
