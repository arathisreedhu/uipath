"""
Custom entropy calculator with time-to-crack estimates.
"""

import math
import string
from typing import Dict


class EntropyCalculator:
    """
    Calculates password entropy and provides crack time estimates.
    """
    
    # Common attack scenarios (guesses per second)
    ATTACK_SCENARIOS = {
        'online_throttled': 10,  # 10 guesses/sec (typical web service with throttling)
        'online_unthrottled': 1000,  # 1000 guesses/sec (no rate limiting)
        'offline_slow': 10_000_000,  # 10M guesses/sec (bcrypt, scrypt)
        'offline_fast': 100_000_000_000,  # 100B guesses/sec (MD5, SHA1 on GPU farm)
    }
    
    def calculate(self, password: str) -> Dict:
        """
        Calculate entropy and time-to-crack estimates.
        
        Args:
            password: The password to analyze
            
        Returns:
            Dictionary with entropy metrics
        """
        if not password:
            return {'entropy_bits': 0, 'pool_size': 0}
        
        # Determine character pool size
        pool_size = self._calculate_pool_size(password)
        
        # Calculate entropy in bits
        entropy_bits = len(password) * math.log2(pool_size)
        
        # Calculate number of possible combinations
        combinations = pool_size ** len(password)
        
        # Estimate time to crack under different scenarios
        crack_times = {}
        for scenario, guesses_per_sec in self.ATTACK_SCENARIOS.items():
            seconds = combinations / (2 * guesses_per_sec)  # Average case (half the space)
            crack_times[scenario] = self._format_time(seconds)
        
        return {
            'entropy_bits': entropy_bits,
            'pool_size': pool_size,
            'total_combinations': combinations,
            'crack_times': crack_times,
            'strength_rating': self._rate_entropy(entropy_bits)
        }
    
    def _calculate_pool_size(self, password: str) -> int:
        """Determine the character pool size based on what's used."""
        pool_size = 0
        
        has_lowercase = any(c in string.ascii_lowercase for c in password)
        has_uppercase = any(c in string.ascii_uppercase for c in password)
        has_digits = any(c in string.digits for c in password)
        has_special = any(c in string.punctuation for c in password)
        has_space = ' ' in password
        
        if has_lowercase:
            pool_size += 26
        if has_uppercase:
            pool_size += 26
        if has_digits:
            pool_size += 10
        if has_special:
            pool_size += len(string.punctuation)
        if has_space:
            pool_size += 1
        
        return pool_size if pool_size > 0 else 1
    
    def _format_time(self, seconds: float) -> str:
        """Format time duration in human-readable format."""
        if seconds < 1:
            return "instant"
        elif seconds < 60:
            return f"{seconds:.0f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.0f} minutes"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} hours"
        elif seconds < 31536000:
            return f"{seconds/86400:.1f} days"
        elif seconds < 3153600000:
            return f"{seconds/31536000:.1f} years"
        elif seconds < 31536000000:
            return f"{seconds/31536000/100:.1f} centuries"
        else:
            return "centuries+"
    
    def _rate_entropy(self, entropy_bits: float) -> str:
        """Rate password strength based on entropy."""
        if entropy_bits < 28:
            return "Very Weak"
        elif entropy_bits < 36:
            return "Weak"
        elif entropy_bits < 50:
            return "Fair"
        elif entropy_bits < 60:
            return "Good"
        elif entropy_bits < 80:
            return "Strong"
        else:
            return "Very Strong"
