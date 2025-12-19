#!/usr/bin/env python3
"""
Main entry point for Password Analyzer package.
Provides shortcuts to CLI and GUI interfaces.
"""

import sys
import argparse


def main():
    """Main entry point with interface selection."""
    parser = argparse.ArgumentParser(
        description="Password Strength Analyzer",
        epilog="Use 'cli' for command-line interface or 'gui' for graphical interface"
    )
    
    parser.add_argument(
        'interface',
        nargs='?',
        choices=['cli', 'gui'],
        default='gui',
        help='Interface to launch (default: gui)'
    )
    
    args = parser.parse_args()
    
    if args.interface == 'cli':
        from password_analyzer.cli import main as cli_main
        cli_main()
    else:
        from password_analyzer.gui import main as gui_main
        gui_main()


if __name__ == '__main__':
    main()
