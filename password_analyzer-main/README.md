# Password Strength Analyzer + User-Safe Wordlist Generator

A defensive security tool for password analysis, education, and authorized security testing. This tool is designed to help users understand password vulnerabilities and improve their password security hygiene.

## ⚠️ IMPORTANT: ETHICAL USE ONLY

**This tool is intended for:**
- ✅ Analyzing YOUR OWN passwords
- ✅ Educational purposes and security awareness
- ✅ Authorized penetration testing with written permission
- ✅ Personal security hygiene improvement

**This tool is NOT for:**
- ❌ Unauthorized access attempts
- ❌ Password cracking without authorization
- ❌ Distribution of attack-ready wordlists
- ❌ Any illegal activity

By using this tool, you agree to use it only for authorized and ethical purposes.

## Features

### 🔐 Core Password Analysis
- **zxcvbn Integration**: Industry-standard password strength evaluation
- **Custom Entropy Calculator**: Detailed bit-strength analysis with multiple attack scenarios
- **Pattern Detection**: Identifies common weaknesses including:
  - Repeated sequences
  - Keyboard patterns
  - Date patterns
  - Sequential characters
  - Leet speak substitutions
- **Crack Time Estimates**: Shows how long it would take to crack under various scenarios

### 👤 Personalized Security Analysis
- Accept user-provided contextual information (name, email, birthdate, etc.)
- Detect if passwords contain personal information
- Generate educational "avoid list" showing risky patterns

### 📚 Educational Wordlist Generator
- Produces small, clearly-labeled educational wordlists
- Shows example transformations (how attackers think)
- Includes security recommendations and best practices
- Limited to 200 entries (not attack-ready)
- Requires explicit authorization confirmation

### 💻 Dual Interface
- **CLI**: Command-line interface with batch processing
- **GUI**: User-friendly tkinter interface

### 🛡️ Built-in Safety Features
- EULA acceptance on first run
- Action logging for audit trail
- Export confirmation requirements
- No network functionality (all local)
- Prominent warnings before sensitive operations

## Installation

### Requirements
- Python 3.10 or higher
- pip package manager

### Install Dependencies

```powershell
cd d:\password_analyzer
pip install -r requirements.txt
```

### Install Package (Optional)

```powershell
pip install -e .
```

## Usage

### Command-Line Interface (CLI)

#### Analyze a Single Password

```powershell
python -m password_analyzer.cli analyze "MyP@ssw0rd" --verbose
```

With contextual information:

```powershell
python -m password_analyzer.cli analyze "john1990" --user-inputs john 1990 john@email.com
```

#### Batch Analysis

Create a text file with one password per line (e.g., `passwords.txt`):

```
password123
MyP@ssw0rd
Tr0ub4dor&3
```

Then run:

```powershell
python -m password_analyzer.cli batch passwords.txt --user-inputs john smith --output results.txt --verbose
```

#### Generate Educational Wordlist

```powershell
python -m password_analyzer.cli generate-wordlist --user-inputs john smith mydog 1990 --export --confirm-authorized --output my_wordlist.txt
```

**Important:** The `--confirm-authorized` flag is REQUIRED to export wordlists.

### Graphical User Interface (GUI)

Launch the GUI:

```powershell
python -m password_analyzer.gui
```

The GUI provides three tabs:

1. **Analyze Password**: Single password analysis with real-time feedback
2. **Batch Analysis**: Upload and analyze multiple passwords
3. **Educational Wordlist**: Generate wordlists with authorization confirmation

## Example Output

### Password Analysis Example

```
================================================================================
PASSWORD ANALYSIS REPORT
================================================================================

📊 Overall Risk Level: CRITICAL
🔢 Password Length: 8 characters
⭐ zxcvbn Score: 0/4

🚨 CRITICAL WARNING: Password contains personal information!
   Matched items: john, 1990

⏱️  Estimated Crack Times:
   Online (throttled): 8 minutes
   Online (no throttle): less than a second
   Offline (slow hash): less than a second
   Offline (fast hash): less than a second

💡 Recommendations:
   ⚠️  This is a very common password
   💡 Add another word or two. Uncommon words are better.
   🚨 CRITICAL: Password contains personal information: john, 1990
   📅 Avoid dates (birthdays, anniversaries) as they're easily guessable
   🎯 Best practice: Use a passphrase (4+ random words) or a password manager
```

## Project Structure

```
password_analyzer/
├── password_analyzer/
│   ├── __init__.py           # Package initialization
│   ├── analyzer.py           # Core password analysis
│   ├── entropy.py            # Entropy calculation
│   ├── pattern_detector.py  # Pattern detection
│   ├── wordlist_generator.py # Educational wordlist generation
│   ├── eula.py               # EULA and safety management
│   ├── cli.py                # Command-line interface
│   └── gui.py                # Graphical user interface
├── tests/
│   ├── test_analyzer.py
│   ├── test_entropy.py
│   ├── test_pattern_detector.py
│   ├── test_wordlist_generator.py
│   └── test_eula.py
├── examples/
│   └── sample_passwords.txt
├── README.md
├── requirements.txt
├── setup.py
└── LICENSE
```

## Running Tests

```powershell
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=password_analyzer --cov-report=html

# Run specific test file
pytest tests/test_analyzer.py -v
```

## How It Works

### Password Strength Evaluation

1. **zxcvbn Analysis**: Uses the battle-tested zxcvbn library to evaluate password strength based on pattern matching and entropy estimation.

2. **Custom Entropy Calculation**: Calculates entropy in bits based on character pool size and password length. Formula: `entropy = length × log₂(pool_size)`

3. **Pattern Detection**: Scans for common weaknesses that reduce effective entropy:
   - Repeated characters (aaa, 111)
   - Keyboard patterns (qwerty, asdf)
   - Sequential patterns (123, abc)
   - Date patterns (1990, 01/01/2020)
   - Leet speak substitutions (p@ssw0rd)

4. **Contextual Risk Analysis**: Checks if password contains user-specific information that makes it vulnerable to targeted attacks.

### Time-to-Crack Estimates

The tool provides estimates for four attack scenarios:

- **Online Throttled** (10 guesses/sec): Typical web service with rate limiting
- **Online Unthrottled** (1,000 guesses/sec): No rate limiting
- **Offline Slow** (10M guesses/sec): Strong hashing (bcrypt, scrypt)
- **Offline Fast** (100B guesses/sec): Weak hashing on GPU farm (MD5, SHA1)

### Educational Wordlist Generation

The wordlist generator creates a SMALL, educational file that includes:

1. **Contextual Items**: User-supplied personal information to avoid
2. **Example Transformations**: Limited examples showing how attackers modify words
3. **Security Recommendations**: Best practices for strong passwords

**Important**: The generator is intentionally limited to ~200 entries to prevent creation of attack-ready lists.

## Security and Privacy

- ✅ **No Network Access**: All processing is local
- ✅ **Audit Logging**: Actions are logged locally for accountability
- ✅ **EULA Enforcement**: Must accept terms on first run
- ✅ **Export Confirmation**: Wordlist export requires explicit authorization
- ✅ **Educational Focus**: Design prevents creation of large attack wordlists

## Best Practices Recommendations

Based on the analysis, the tool recommends:

1. **Use Passphrases**: 4-6 random, unrelated words (e.g., "correct-horse-battery-staple")
2. **Use a Password Manager**: Generate unique 16+ character passwords for each account
3. **Avoid Personal Information**: No names, birthdays, addresses, etc.
4. **Avoid Common Patterns**: No keyboard patterns, dates, or simple substitutions
5. **Enable 2FA**: Two-factor authentication adds critical extra security
6. **Aim for Length**: 12+ characters for passphrases, 16+ for random passwords

## Legal Disclaimer

This software is provided "AS IS" without warranty of any kind. The authors are not responsible for any misuse of this tool. Users are solely responsible for ensuring their use complies with all applicable laws and regulations.

Unauthorized computer access is illegal under the Computer Fraud and Abuse Act (CFAA) and similar laws worldwide. Always obtain proper authorization before conducting security testing.

## License

MIT License - See LICENSE file for details

## Contributing

This is an educational project. If you'd like to contribute:

1. Ensure contributions maintain the defensive/educational focus
2. Do not add features that facilitate unauthorized access
3. Include tests for new functionality
4. Update documentation

## Support and Contact

For questions about ethical use, refer to the EULA included with the software.

## Acknowledgments

- **zxcvbn** by Dropbox: Industry-leading password strength estimation
- **NLTK**: Natural Language Toolkit for text processing
- Security research community for password analysis best practices

## Version History

### v1.0.0 (2025-10-21)
- Initial release
- Core password analysis with zxcvbn integration
- Custom entropy calculator
- Pattern detection system
- Educational wordlist generator
- CLI and GUI interfaces
- Comprehensive safety controls
- Full test suite

---

**Remember: Use this tool responsibly and only for authorized purposes.**
