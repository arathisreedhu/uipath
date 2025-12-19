"""
EULA and safety/ethics enforcement.
"""

import os
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class EULAManager:
    """
    Manages end-user license agreement and ethical use confirmations.
    """
    
    def __init__(self, config_dir: str = None):
        """Initialize EULA manager with config directory."""
        if config_dir is None:
            config_dir = os.path.join(Path.home(), '.password_analyzer')
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.eula_file = self.config_dir / 'eula_accepted.txt'
        self.log_file = self.config_dir / 'usage.log'
    
    def check_eula_accepted(self) -> bool:
        """Check if user has accepted EULA."""
        return self.eula_file.exists()
    
    def get_eula_text(self) -> str:
        """Get the full EULA text."""
        return """
================================================================================
        PASSWORD STRENGTH ANALYZER - END USER LICENSE AGREEMENT
================================================================================

PLEASE READ CAREFULLY BEFORE USING THIS SOFTWARE

This Password Strength Analyzer tool is provided for DEFENSIVE SECURITY,
EDUCATION, and AUTHORIZED TESTING purposes only.

1. PERMITTED USES:
   ✓ Analyzing YOUR OWN passwords for security weaknesses
   ✓ Educational purposes and security awareness training
   ✓ Authorized penetration testing with proper written authorization
   ✓ Security research in controlled, legal environments
   ✓ Helping others understand password security (with their consent)

2. PROHIBITED USES:
   ✗ Attempting unauthorized access to any computer system
   ✗ Password cracking without explicit authorization
   ✗ Creating wordlists for distribution or malicious purposes
   ✗ Any activity that violates local, state, or federal laws
   ✗ Testing passwords that do not belong to you without permission

3. LEGAL DISCLAIMER:
   - Unauthorized computer access is ILLEGAL in most jurisdictions
   - Violators may face criminal prosecution and civil liability
   - The Computer Fraud and Abuse Act (CFAA) and similar laws worldwide
     prohibit unauthorized access
   - You are solely responsible for your use of this tool

4. WARRANTY DISCLAIMER:
   This software is provided "AS IS" without warranty of any kind.
   The authors assume no liability for misuse or damages resulting from
   the use of this software.

5. CONSENT TO LOGGING:
   This tool logs usage locally for security audit purposes.
   No data is transmitted to external servers.

6. YOUR AGREEMENT:
   By accepting this agreement, you acknowledge that:
   - You have read and understood these terms
   - You will use this tool ONLY for authorized purposes
   - You understand that unauthorized use is illegal and unethical
   - You accept full responsibility for your actions

================================================================================
"""
    
    def accept_eula(self) -> bool:
        """Record EULA acceptance."""
        try:
            with open(self.eula_file, 'w') as f:
                f.write(f"EULA Accepted: {datetime.now().isoformat()}\n")
                f.write(f"Version: 1.0.0\n")
            
            logger.info("EULA accepted by user")
            self.log_action("EULA accepted")
            return True
        
        except Exception as e:
            logger.error(f"Failed to record EULA acceptance: {e}")
            return False
    
    def log_action(self, action: str, details: str = ""):
        """Log user actions for audit trail."""
        try:
            with open(self.log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                log_entry = f"{timestamp} | {action}"
                if details:
                    log_entry += f" | {details}"
                f.write(log_entry + "\n")
        
        except Exception as e:
            logger.error(f"Failed to log action: {e}")
    
    def get_export_warning(self) -> str:
        """Get warning text for wordlist export."""
        return """
⚠️  WORDLIST EXPORT CONFIRMATION REQUIRED ⚠️

You are about to export an educational wordlist.

IMPORTANT REMINDERS:
• This wordlist is for YOUR OWN password analysis and education
• Using this for unauthorized access attempts is ILLEGAL
• You must have proper authorization for any security testing
• Distributing this for malicious purposes violates the EULA

This action will be logged.

Do you confirm you will use this wordlist ONLY for authorized purposes?
"""
    
    def confirm_export_cli(self) -> bool:
        """
        Get user confirmation for export in CLI mode.
        Requires explicit --confirm-authorized flag.
        """
        print(self.get_export_warning())
        print("\nYou must use --confirm-authorized flag to proceed with export.")
        return False
    
    def confirm_export_gui(self) -> bool:
        """
        This is called by GUI to show warning.
        Actual confirmation is handled by GUI dialog.
        """
        return True
