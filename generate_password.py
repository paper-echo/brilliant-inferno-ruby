#!/usr/bin/env python3
"""
Secure Password Generator

A standalone script to generate secure, random passwords.

Usage:

# Generate a 12-character password and copy to clipboard
python3 generate_password.py -l 12 | pbcopy

# Generate a 24-character password and copy
python3 generate_password.py --length 24 | pbcopy

# Generate a 20-character password without special chars and copy
python3 generate_password.py -l 20 --no-special | pbcopy

"""

import secrets
import string
import argparse
import sys


def generate_password(length=32, use_uppercase=True, use_lowercase=True, 
                     use_digits=True, use_special=True, exclude_similar=False):
    """
    Generate a secure random password.
    
    Args:
        length: Length of the password (default: 32)
        use_uppercase: Include uppercase letters (A-Z)
        use_lowercase: Include lowercase letters (a-z)
        use_digits: Include digits (0-9)
        use_special: Include special characters (!@#$%^&*...)
        exclude_similar: Exclude similar-looking characters (i, l, 1, L, o, 0, O)
    
    Returns:
        A secure random password string
    """
    # Define character sets
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Characters that look similar and might be confused
    similar_chars = "il1Lo0O"
    
    # Build the character pool
    chars = ""
    if use_uppercase:
        chars += uppercase
    if use_lowercase:
        chars += lowercase
    if use_digits:
        chars += digits
    if use_special:
        chars += special
    
    # Remove similar characters if requested
    if exclude_similar:
        chars = ''.join(c for c in chars if c not in similar_chars)
    
    # Ensure we have at least one character from each selected category
    if not chars:
        raise ValueError("At least one character set must be enabled")
    
    # Validate minimum length
    min_length = sum([use_uppercase, use_lowercase, use_digits, use_special])
    if length < min_length:
        raise ValueError(f"Password length must be at least {min_length} to include all selected character types")
    
    # Generate password ensuring at least one character from each category
    password = []
    
    # Add at least one character from each enabled category
    if use_uppercase:
        password.append(secrets.choice(uppercase))
    if use_lowercase:
        password.append(secrets.choice(lowercase))
    if use_digits:
        password.append(secrets.choice(digits))
    if use_special:
        password.append(secrets.choice(special))
    
    # Fill the rest with random characters from the pool
    while len(password) < length:
        char = secrets.choice(chars)
        if exclude_similar and char in similar_chars:
            continue
        password.append(char)
    
    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def main():
    parser = argparse.ArgumentParser(
        description='Generate a secure random password',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Generate a 32-character password
  %(prog)s -l 16              # Generate a 16-character password
  %(prog)s -l 20 --no-special # Generate without special characters
  %(prog)s -l 24 --exclude-similar # Exclude similar-looking characters
        """
    )
    
    parser.add_argument(
        '-l', '--length',
        type=int,
        default=32,
        help='Password length (default: 32)'
    )
    
    parser.add_argument(
        '--no-uppercase',
        action='store_true',
        help='Exclude uppercase letters'
    )
    
    parser.add_argument(
        '--no-lowercase',
        action='store_true',
        help='Exclude lowercase letters'
    )
    
    parser.add_argument(
        '--no-digits',
        action='store_true',
        help='Exclude digits'
    )
    
    parser.add_argument(
        '--no-special',
        action='store_true',
        help='Exclude special characters'
    )
    
    parser.add_argument(
        '--exclude-similar',
        action='store_true',
        help='Exclude similar-looking characters (i, l, 1, L, o, 0, O)'
    )
    
    parser.add_argument(
        '-c', '--count',
        type=int,
        default=1,
        help='Number of passwords to generate (default: 1)'
    )
    
    parser.add_argument(
        '--copy',
        action='store_true',
        help='Copy password to clipboard (requires pyperclip)'
    )
    
    args = parser.parse_args()
    
    try:
        for i in range(args.count):
            password = generate_password(
                length=args.length,
                use_uppercase=not args.no_uppercase,
                use_lowercase=not args.no_lowercase,
                use_digits=not args.no_digits,
                use_special=not args.no_special,
                exclude_similar=args.exclude_similar
            )
            
            print(password)
            
            # Copy to clipboard if requested
            if args.copy:
                try:
                    import pyperclip
                    pyperclip.copy(password)
                    if args.count == 1:
                        print("(Password copied to clipboard)", file=sys.stderr)
                except ImportError:
                    print("Warning: pyperclip not installed. Install with: pip install pyperclip", file=sys.stderr)
                except Exception as e:
                    print(f"Warning: Could not copy to clipboard: {e}", file=sys.stderr)
    
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

