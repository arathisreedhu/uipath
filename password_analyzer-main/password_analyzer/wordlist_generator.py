"""
Educational wordlist generator with safety controls.
"""

import logging
from typing import List, Set, Dict
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class WordlistGenerator:
    """
    Generates educational wordlists for awareness and authorized testing only.
    Includes prominent safety warnings and limits output size.
    """
    
    MAX_ENTRIES = 200  # Hard limit on wordlist size
    
    def __init__(self):
        self.common_years = [str(year) for year in range(1950, 2026)]
        self.common_suffixes = ['123', '!', '1', '12', '2024', '2025']
        
        # Limited leet speak mappings for educational purposes
        self.leet_map = {
            'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'
        }
    
    def generate_educational_wordlist(
        self,
        user_inputs: List[str],
        output_path: str = "educational_wordlist.txt"
    ) -> Dict[str, any]:
        """
        Generate a small educational wordlist showing password weaknesses.
        
        Args:
            user_inputs: User-provided contextual items
            output_path: Where to save the wordlist
            
        Returns:
            Dictionary with generation statistics
        """
        entries = set()
        
        # Add header warning
        header = self._generate_header()
        
        # Section 1: User contextual items (as-is)
        contextual_section = self._generate_contextual_section(user_inputs)
        entries.update(contextual_section)
        
        # Section 2: Common transformations (educational examples)
        transformation_section = self._generate_transformation_examples(user_inputs)
        entries.update(transformation_section)
        
        # Section 3: Suggestions for better passwords
        suggestions_section = self._generate_suggestions()
        
        # Limit total entries
        entries = list(entries)[:self.MAX_ENTRIES - 10]  # Reserve space for suggestions
        
        # Write to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(header)
                f.write("\n" + "="*80 + "\n")
                f.write("SECTION 1: CONTEXTUAL ITEMS TO AVOID IN PASSWORDS\n")
                f.write("="*80 + "\n\n")
                
                for item in contextual_section:
                    f.write(f"{item}\n")
                
                f.write("\n" + "="*80 + "\n")
                f.write("SECTION 2: EXAMPLE TRANSFORMATIONS (How Attackers Think)\n")
                f.write("="*80 + "\n")
                f.write("These show common mutations attackers try. DON'T use these patterns!\n\n")
                
                for item in transformation_section:
                    f.write(f"{item}\n")
                
                f.write("\n" + "="*80 + "\n")
                f.write("SECTION 3: RECOMMENDED SECURE PASSWORD STRATEGIES\n")
                f.write("="*80 + "\n\n")
                
                for suggestion in suggestions_section:
                    f.write(f"{suggestion}\n")
                
                f.write("\n" + "="*80 + "\n")
                f.write("END OF EDUCATIONAL WORDLIST\n")
                f.write("="*80 + "\n")
            
            logger.info(f"Educational wordlist generated: {output_path} ({len(entries)} entries)")
            
            return {
                'success': True,
                'path': output_path,
                'total_entries': len(entries),
                'contextual_count': len(contextual_section),
                'transformation_count': len(transformation_section)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate wordlist: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_header(self) -> str:
        """Generate prominent warning header."""
        return f"""
{'='*80}
⚠️  EDUCATIONAL WORDLIST - FOR AUTHORIZED USE ONLY ⚠️
{'='*80}

LEGAL NOTICE:
This file is generated for PASSWORD AWARENESS and AUTHORIZED SECURITY TESTING only.

PERMITTED USES:
✓ Testing YOUR OWN passwords for weaknesses
✓ Educational purposes to understand password vulnerabilities
✓ Authorized penetration testing with written permission
✓ Security awareness training

PROHIBITED USES:
✗ Unauthorized access attempts
✗ Password cracking without authorization
✗ Distribution for malicious purposes
✗ Any illegal activity

BY USING THIS FILE, YOU ACKNOWLEDGE:
- You will use this ONLY for authorized purposes
- You understand unauthorized access is illegal
- You accept full responsibility for your actions

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Tool: Password Strength Analyzer v1.0.0
"""
    
    def _generate_contextual_section(self, user_inputs: List[str]) -> Set[str]:
        """Generate list of user contextual items."""
        items = set()
        
        for item in user_inputs:
            if item and len(item) >= 3:
                items.add(item.strip())
                items.add(item.lower().strip())
                items.add(item.upper().strip())
                items.add(item.capitalize().strip())
        
        return items
    
    def _generate_transformation_examples(self, user_inputs: List[str]) -> Set[str]:
        """
        Generate LIMITED educational examples of how attackers transform words.
        Intentionally kept small to avoid creating attack-ready lists.
        """
        examples = set()
        
        # Only process first few items to keep list small
        for item in user_inputs[:5]:
            if not item or len(item) < 3:
                continue
            
            item = item.strip()
            
            # Example 1: Add common years
            for year in random.sample(self.common_years, min(3, len(self.common_years))):
                examples.add(f"{item}{year}")
            
            # Example 2: Add common suffixes
            for suffix in self.common_suffixes[:3]:
                examples.add(f"{item}{suffix}")
            
            # Example 3: Simple leet speak (just ONE example)
            leet_version = self._apply_leet_speak(item, max_substitutions=2)
            if leet_version != item:
                examples.add(leet_version)
            
            # Example 4: First letter uppercase
            examples.add(item.capitalize())
            
            # Limit examples per item
            if len(examples) >= 50:
                break
        
        return examples
    
    def _apply_leet_speak(self, text: str, max_substitutions: int = 2) -> str:
        """Apply limited leet speak transformations."""
        result = list(text.lower())
        substitutions = 0
        
        for i, char in enumerate(result):
            if char in self.leet_map and substitutions < max_substitutions:
                result[i] = self.leet_map[char]
                substitutions += 1
        
        return ''.join(result)
    
    def _generate_suggestions(self) -> List[str]:
        """Generate secure password suggestions."""
        return [
            "",
            "INSTEAD OF weak passwords, USE THESE STRATEGIES:",
            "",
            "1. PASSPHRASES (Recommended):",
            "   - Combine 4-6 random, unrelated words",
            "   - Example: correct-horse-battery-staple",
            "   - Easy to remember, hard to crack",
            "",
            "2. PASSWORD MANAGER GENERATED:",
            "   - Use a password manager (e.g., Bitwarden, 1Password, KeePass)",
            "   - Generate unique 16+ character passwords for each account",
            "   - Example: Kp9$mN2#vL8@wQ5&",
            "",
            "3. DICE WARE METHOD:",
            "   - Use physical dice to randomly select words from a wordlist",
            "   - Ensures true randomness",
            "   - Combine 5-7 words for strong security",
            "",
            "4. AVOID THESE PATTERNS:",
            "   ✗ Personal information (names, birthdays, addresses)",
            "   ✗ Dictionary words with simple substitutions",
            "   ✗ Common sequences (123, abc, qwerty)",
            "   ✗ Keyboard patterns",
            "   ✗ Repeating the same password across sites",
            "",
            "5. ENABLE TWO-FACTOR AUTHENTICATION (2FA):",
            "   - Even strong passwords benefit from 2FA",
            "   - Use authenticator apps (not SMS when possible)",
            "",
            "REMEMBER: Length + Randomness = Security",
            "Aim for: 12+ characters (passphrases) or 16+ (random passwords)",
            ""
        ]
