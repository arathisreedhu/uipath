# Password Analyzer - Quick Start Examples

## Example 1: Analyze a Single Password

```powershell
python -m password_analyzer.cli analyze "MyP@ssw0rd123"
```

## Example 2: Analyze with User Context

```powershell
python -m password_analyzer.cli analyze "john1990" --user-inputs john 1990 john@email.com
```

## Example 3: Batch Analysis

```powershell
python -m password_analyzer.cli batch examples/sample_passwords.txt --verbose
```

## Example 4: Batch Analysis with Context

```powershell
python -m password_analyzer.cli batch examples/sample_passwords.txt --user-inputs john smith company --output batch_results.txt
```

## Example 5: Generate Educational Wordlist

```powershell
python -m password_analyzer.cli generate-wordlist --user-inputs john smith mydog fluffy 1990 company --export --confirm-authorized
```

## Example 6: Launch GUI

```powershell
python -m password_analyzer.gui
```

## Example 7: Test Strong vs Weak Passwords

```powershell
# Weak password
python -m password_analyzer.cli analyze "password123"

# Medium password
python -m password_analyzer.cli analyze "MyP@ssw0rd"

# Strong password
python -m password_analyzer.cli analyze "correct-horse-battery-staple"

# Very strong password
python -m password_analyzer.cli analyze "Tr0ub4dor&3-Xqr9$Kp2"
```

## Example 8: Understanding Pattern Detection

```powershell
# Repeated sequences
python -m password_analyzer.cli analyze "aaabbb111" --verbose

# Keyboard pattern
python -m password_analyzer.cli analyze "qwerty123" --verbose

# Date pattern
python -m password_analyzer.cli analyze "password1990" --verbose

# Leet speak
python -m password_analyzer.cli analyze "p4ssw0rd" --verbose
```

## Example 9: Personal Information Detection

```powershell
python -m password_analyzer.cli analyze "johnsmith1990" --user-inputs john smith 1990 --verbose
```

## Example 10: Running Tests

```powershell
# Install pytest if not already installed
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_analyzer.py -v

# Run with coverage report
pytest tests/ --cov=password_analyzer --cov-report=html
```
