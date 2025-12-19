"""
Demonstration script showing all features of the Password Analyzer.
"""

from password_analyzer import PasswordAnalyzer, WordlistGenerator
from password_analyzer.eula import EULAManager
import json


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def demo_basic_analysis():
    """Demonstrate basic password analysis."""
    print_section("DEMO 1: Basic Password Analysis")
    
    analyzer = PasswordAnalyzer()
    
    # Analyze a weak password
    print("Analyzing: 'password123'\n")
    result = analyzer.analyze("password123")
    
    print(f"Score: {result['zxcvbn_score']}/4")
    print(f"Risk Level: {result['overall_risk']}")
    print(f"Crack time (online): {result['crack_times_display'].get('online_throttling', 'N/A')}")
    print(f"\nTop Recommendations:")
    for i, rec in enumerate(result['recommendations'][:3], 1):
        print(f"  {i}. {rec}")


def demo_strong_password():
    """Demonstrate analysis of a strong password."""
    print_section("DEMO 2: Strong Password Analysis")
    
    analyzer = PasswordAnalyzer()
    
    print("Analyzing: 'correct-horse-battery-staple'\n")
    result = analyzer.analyze("correct-horse-battery-staple")
    
    print(f"Score: {result['zxcvbn_score']}/4")
    print(f"Risk Level: {result['overall_risk']}")
    
    if result['entropy']:
        print(f"Entropy: {result['entropy']['entropy_bits']:.1f} bits")
        print(f"Strength Rating: {result['entropy']['strength_rating']}")
    
    print(f"Crack time (offline fast): {result['crack_times_display'].get('offline_fast_hashing_1e10_per_second', 'N/A')}")


def demo_contextual_analysis():
    """Demonstrate contextual information detection."""
    print_section("DEMO 3: Contextual Information Detection")
    
    analyzer = PasswordAnalyzer()
    
    user_context = ["john", "smith", "1990", "mydog"]
    
    print(f"User context: {', '.join(user_context)}")
    print("\nAnalyzing: 'john1990'\n")
    
    result = analyzer.analyze("john1990", user_inputs=user_context)
    
    print(f"Score: {result['zxcvbn_score']}/4")
    print(f"Risk Level: {result['overall_risk']}")
    print(f"Contains Personal Info: {result['has_contextual_risk']}")
    
    if result['contextual_matches']:
        print(f"Matched Items: {', '.join(result['contextual_matches'])}")


def demo_pattern_detection():
    """Demonstrate pattern detection capabilities."""
    print_section("DEMO 4: Pattern Detection")
    
    analyzer = PasswordAnalyzer()
    
    test_passwords = [
        ("qwerty123", "Keyboard Pattern"),
        ("password111", "Repeated Sequences"),
        ("abc123def", "Sequential Patterns"),
        ("p4ssw0rd", "Leet Speak"),
    ]
    
    for password, expected_pattern in test_passwords:
        result = analyzer.analyze(password)
        patterns = result['patterns_detected']
        
        print(f"Password: '{password}' (Testing: {expected_pattern})")
        print(f"  Score: {result['zxcvbn_score']}/4")
        
        if patterns['keyboard_patterns']:
            print(f"  ⌨️  Keyboard patterns: {patterns['keyboard_patterns']}")
        if patterns['repeated_sequences']:
            print(f"  🔄 Repeated sequences: {patterns['repeated_sequences']}")
        if patterns['sequential']:
            print(f"  🔢 Sequential: {patterns['sequential']}")
        if patterns['leet_speak']:
            print(f"  🔡 Leet speak: Detected")
        
        print()


def demo_batch_analysis():
    """Demonstrate batch password analysis."""
    print_section("DEMO 5: Batch Analysis")
    
    analyzer = PasswordAnalyzer()
    
    passwords = [
        "123456",
        "password",
        "MyP@ssw0rd123",
        "correct-horse-battery-staple",
        "Tr0ub4dor&3"
    ]
    
    print(f"Analyzing {len(passwords)} passwords...\n")
    
    results = analyzer.batch_analyze(passwords)
    
    # Calculate statistics
    risk_counts = {}
    for result in results:
        risk = result['overall_risk']
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    print("Risk Distribution:")
    for risk, count in sorted(risk_counts.items()):
        percentage = count / len(results) * 100
        print(f"  {risk}: {count} ({percentage:.1f}%)")
    
    print("\nDetailed Results:")
    for i, (pwd, result) in enumerate(zip(passwords, results), 1):
        masked_pwd = pwd[:3] + "*" * (len(pwd) - 3)
        print(f"  {i}. {masked_pwd}: Score {result['zxcvbn_score']}/4, Risk: {result['overall_risk']}")


def demo_entropy_calculator():
    """Demonstrate entropy calculation details."""
    print_section("DEMO 6: Detailed Entropy Analysis")
    
    analyzer = PasswordAnalyzer()
    
    print("Comparing entropy across different password types:\n")
    
    test_cases = [
        ("abc", "Lowercase only"),
        ("Abc123", "Mixed case + digits"),
        ("Abc@123!", "Full character set"),
        ("ThisIsALongPassword", "Long passphrase")
    ]
    
    for password, description in test_cases:
        result = analyzer.analyze(password, use_entropy=True)
        entropy = result['entropy']
        
        print(f"{description}: '{password}'")
        print(f"  Entropy: {entropy['entropy_bits']:.1f} bits")
        print(f"  Character Pool: {entropy['pool_size']}")
        print(f"  Rating: {entropy['strength_rating']}")
        print(f"  Crack time (offline slow): {entropy['crack_times']['offline_slow']}")
        print()


def demo_wordlist_preview():
    """Demonstrate wordlist generation concept (without actually generating)."""
    print_section("DEMO 7: Educational Wordlist Concept")
    
    print("Educational wordlist generator would create a file with:")
    print()
    print("1. CONTEXTUAL ITEMS TO AVOID")
    print("   - User-provided personal information")
    print("   - Case variations (john, John, JOHN)")
    print()
    print("2. EXAMPLE TRANSFORMATIONS (Educational Only)")
    print("   - Common year appends (john1990, john2024)")
    print("   - Simple suffixes (john123, john!)")
    print("   - Limited leet speak examples (j0hn)")
    print()
    print("3. SECURITY RECOMMENDATIONS")
    print("   - Passphrase strategies")
    print("   - Password manager recommendations")
    print("   - 2FA importance")
    print()
    print("⚠️  Limited to ~200 entries maximum")
    print("⚠️  Requires explicit authorization confirmation")
    print("⚠️  Includes prominent legal warnings")


def demo_eula_features():
    """Demonstrate EULA and safety features."""
    print_section("DEMO 8: Safety & Ethics Features")
    
    eula = EULAManager(config_dir="demo_config")
    
    print("Safety features included:")
    print()
    print("✅ EULA acceptance required on first run")
    print("✅ Clear permitted and prohibited uses")
    print("✅ Action logging for audit trail")
    print("✅ Export confirmation requirements")
    print("✅ No network functionality (all local)")
    print("✅ Prominent warnings before sensitive operations")
    print()
    
    print("EULA covers:")
    print("  • Permitted uses (own passwords, education, authorized testing)")
    print("  • Prohibited uses (unauthorized access, malicious distribution)")
    print("  • Legal disclaimers (CFAA compliance, liability)")
    print("  • User responsibilities")
    
    # Cleanup demo config
    import shutil
    if eula.config_dir.exists():
        shutil.rmtree(eula.config_dir)


def demo_recommendations():
    """Show password strength recommendations."""
    print_section("DEMO 9: Password Strength Recommendations")
    
    analyzer = PasswordAnalyzer()
    
    print("Getting recommendations for weak password:\n")
    
    result = analyzer.analyze("password", user_inputs=["password"])
    
    print("Recommendations:")
    for rec in result['recommendations']:
        print(f"  • {rec}")


def main():
    """Run all demonstrations."""
    print("\n" + "="*80)
    print(" "*20 + "PASSWORD ANALYZER - FEATURE DEMONSTRATION")
    print("="*80)
    print("\nThis demo showcases the defensive security features of Password Analyzer.")
    print("All features are designed for educational and authorized testing only.")
    print("\n⚠️  FOR DEMONSTRATION PURPOSES ONLY - Use responsibly!")
    
    input("\nPress Enter to begin demonstrations...")
    
    try:
        demo_basic_analysis()
        input("\nPress Enter to continue...")
        
        demo_strong_password()
        input("\nPress Enter to continue...")
        
        demo_contextual_analysis()
        input("\nPress Enter to continue...")
        
        demo_pattern_detection()
        input("\nPress Enter to continue...")
        
        demo_batch_analysis()
        input("\nPress Enter to continue...")
        
        demo_entropy_calculator()
        input("\nPress Enter to continue...")
        
        demo_wordlist_preview()
        input("\nPress Enter to continue...")
        
        demo_eula_features()
        input("\nPress Enter to continue...")
        
        demo_recommendations()
        
        print_section("DEMONSTRATION COMPLETE")
        print("Thank you for exploring Password Analyzer!")
        print("\nFor actual usage:")
        print("  CLI: python -m password_analyzer.cli --help")
        print("  GUI: python -m password_analyzer.gui")
        print("\nRemember: Use only for authorized purposes!")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Exiting...")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")


if __name__ == '__main__':
    main()
