#!/usr/bin/env python3
"""
CLI interface for Password Strength Analyzer.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List

from password_analyzer import PasswordAnalyzer, WordlistGenerator
from password_analyzer.eula import EULAManager


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def print_analysis_result(result: dict, verbose: bool = False):
    """Print password analysis result in a readable format."""
    print("\n" + "="*80)
    print("PASSWORD ANALYSIS REPORT")
    print("="*80)
    
    # Basic info
    print(f"\n📊 Overall Risk Level: {result['overall_risk']}")
    print(f"🔢 Password Length: {result['password_length']} characters")
    print(f"⭐ zxcvbn Score: {result['zxcvbn_score']}/4")
    
    # Critical warnings
    if result['has_contextual_risk']:
        print(f"\n🚨 CRITICAL WARNING: Password contains personal information!")
        print(f"   Matched items: {', '.join(result['contextual_matches'])}")
    
    # Crack time estimates
    print(f"\n⏱️  Estimated Crack Times:")
    crack_times = result['crack_times_display']
    print(f"   Online (throttled): {crack_times.get('online_throttling', 'N/A')}")
    print(f"   Online (no throttle): {crack_times.get('online_no_throttling', 'N/A')}")
    print(f"   Offline (slow hash): {crack_times.get('offline_slow_hashing_1e4_per_second', 'N/A')}")
    print(f"   Offline (fast hash): {crack_times.get('offline_fast_hashing_1e10_per_second', 'N/A')}")
    
    # Entropy information
    if result['entropy'] and verbose:
        print(f"\n🔐 Entropy Analysis:")
        print(f"   Entropy: {result['entropy']['entropy_bits']:.1f} bits")
        print(f"   Character Pool: {result['entropy']['pool_size']}")
        print(f"   Strength Rating: {result['entropy']['strength_rating']}")
    
    # Pattern detection
    if verbose:
        patterns = result['patterns_detected']
        if any(patterns.values()):
            print(f"\n🔍 Detected Patterns:")
            if patterns['repeated_sequences']:
                print(f"   - Repeated sequences: {patterns['repeated_sequences']}")
            if patterns['keyboard_patterns']:
                print(f"   - Keyboard patterns: {patterns['keyboard_patterns']}")
            if patterns['dates']:
                print(f"   - Date patterns: {patterns['dates']}")
            if patterns['sequential']:
                print(f"   - Sequential patterns: {patterns['sequential']}")
            if patterns['leet_speak']:
                print(f"   - Leet speak detected: Yes")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    for rec in result['recommendations']:
        print(f"   {rec}")
    
    print("\n" + "="*80 + "\n")


def analyze_password_command(args):
    """Handle single password analysis."""
    analyzer = PasswordAnalyzer()
    
    result = analyzer.analyze(
        args.password,
        user_inputs=args.user_inputs,
        use_entropy=not args.no_entropy
    )
    
    print_analysis_result(result, verbose=args.verbose)


def batch_analyze_command(args):
    """Handle batch password analysis from file."""
    if not Path(args.file).exists():
        print(f"❌ Error: File not found: {args.file}")
        sys.exit(1)
    
    # Read passwords (filter out comments)
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            passwords = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)
    
    print(f"📁 Analyzing {len(passwords)} passwords from {args.file}...")
    
    analyzer = PasswordAnalyzer()
    results = analyzer.batch_analyze(passwords, user_inputs=args.user_inputs)
    
    # Summary statistics
    risk_counts = {}
    for result in results:
        risk = result['overall_risk']
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    print("\n" + "="*80)
    print("BATCH ANALYSIS SUMMARY")
    print("="*80)
    print(f"Total passwords analyzed: {len(results)}")
    print(f"\nRisk Distribution:")
    for risk, count in sorted(risk_counts.items()):
        print(f"  {risk}: {count} ({count/len(results)*100:.1f}%)")
    
    # Detailed results if verbose
    if args.verbose:
        print("\n" + "="*80)
        print("DETAILED RESULTS")
        print("="*80)
        for i, result in enumerate(results, 1):
            print(f"\nPassword #{i}:")
            print_analysis_result(result, verbose=False)
    
    # Export results if requested
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write("Password Strength Analysis Report\n")
                f.write(f"Generated: {Path(args.file).name}\n")
                f.write("="*80 + "\n\n")
                
                for i, result in enumerate(results, 1):
                    f.write(f"Password #{i}:\n")
                    f.write(f"  Score: {result['zxcvbn_score']}/4\n")
                    f.write(f"  Risk: {result['overall_risk']}\n")
                    f.write(f"  Length: {result['password_length']}\n")
                    if result['has_contextual_risk']:
                        f.write(f"  ⚠️  Contains personal info: {result['contextual_matches']}\n")
                    f.write("\n")
            
            print(f"\n✅ Results exported to: {args.output}")
        
        except Exception as e:
            print(f"❌ Error exporting results: {e}")


def generate_wordlist_command(args):
    """Handle educational wordlist generation."""
    eula = EULAManager()
    
    # Check for authorization
    if not args.confirm_authorized:
        print(eula.get_export_warning())
        print("\n❌ Export requires --confirm-authorized flag.")
        print("Example: --export --confirm-authorized")
        sys.exit(1)
    
    if not args.user_inputs:
        print("❌ Error: --user-inputs required for wordlist generation")
        print("Example: --user-inputs john,smith,john@email.com")
        sys.exit(1)
    
    # Log the action
    eula.log_action("Wordlist export", f"Items: {len(args.user_inputs)}")
    
    # Generate wordlist
    generator = WordlistGenerator()
    result = generator.generate_educational_wordlist(
        args.user_inputs,
        output_path=args.output or "educational_wordlist.txt"
    )
    
    if result['success']:
        print(f"\n✅ Educational wordlist generated successfully!")
        print(f"   Path: {result['path']}")
        print(f"   Total entries: {result['total_entries']}")
        print(f"   Contextual items: {result['contextual_count']}")
        print(f"   Example transformations: {result['transformation_count']}")
        print(f"\n⚠️  Remember: Use ONLY for authorized purposes!")
    else:
        print(f"\n❌ Error generating wordlist: {result.get('error', 'Unknown error')}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Password Strength Analyzer - Defensive Security Tool",
        epilog="For authorized use only. See EULA for terms."
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Password Analyzer 1.0.0'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze a single password'
    )
    analyze_parser.add_argument(
        'password',
        help='Password to analyze'
    )
    analyze_parser.add_argument(
        '--user-inputs',
        nargs='*',
        default=[],
        help='User contextual items (name, email, etc.)'
    )
    analyze_parser.add_argument(
        '--no-entropy',
        action='store_true',
        help='Skip custom entropy calculation'
    )
    
    # Batch analyze command
    batch_parser = subparsers.add_parser(
        'batch',
        help='Analyze multiple passwords from a file'
    )
    batch_parser.add_argument(
        'file',
        help='File containing passwords (one per line)'
    )
    batch_parser.add_argument(
        '--user-inputs',
        nargs='*',
        default=[],
        help='User contextual items'
    )
    batch_parser.add_argument(
        '--output',
        help='Export results to file'
    )
    
    # Generate wordlist command
    wordlist_parser = subparsers.add_parser(
        'generate-wordlist',
        help='Generate educational wordlist'
    )
    wordlist_parser.add_argument(
        '--user-inputs',
        nargs='*',
        help='User contextual items (REQUIRED)'
    )
    wordlist_parser.add_argument(
        '--output',
        default='educational_wordlist.txt',
        help='Output file path'
    )
    wordlist_parser.add_argument(
        '--export',
        action='store_true',
        help='Enable export (requires --confirm-authorized)'
    )
    wordlist_parser.add_argument(
        '--confirm-authorized',
        action='store_true',
        help='Confirm authorized use of exported wordlist'
    )
    
    args = parser.parse_args()
    
    # Setup
    setup_logging(args.verbose)
    eula = EULAManager()
    
    # Check EULA acceptance
    if not eula.check_eula_accepted():
        print(eula.get_eula_text())
        response = input("\nDo you accept these terms? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print("EULA not accepted. Exiting.")
            sys.exit(1)
        
        if not eula.accept_eula():
            print("Failed to record EULA acceptance. Exiting.")
            sys.exit(1)
        
        print("\n✅ EULA accepted. Thank you for using this tool responsibly.\n")
    
    # Route to appropriate command
    if args.command == 'analyze':
        eula.log_action("Password analysis", f"Length: {len(args.password)}")
        analyze_password_command(args)
    
    elif args.command == 'batch':
        eula.log_action("Batch analysis", f"File: {args.file}")
        batch_analyze_command(args)
    
    elif args.command == 'generate-wordlist':
        if args.export:
            generate_wordlist_command(args)
        else:
            print("❌ Error: --export flag required for wordlist generation")
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
