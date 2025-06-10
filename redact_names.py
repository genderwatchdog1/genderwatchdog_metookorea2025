#!/usr/bin/env python3
"""
Script to recursively redact specified strings from files in a directory.
Each redacted string is replaced with asterisks (*) of the same length.

Usage:
    python redact_names.py /path/to/directory "string1" "string2" "string3"
"""

import os
import argparse
import sys
from pathlib import Path


def is_text_file(file_path):
    """
    Check if a file is likely a text file by attempting to read a small portion.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1024)
        return True
    except (UnicodeDecodeError, PermissionError):
        return False


def redact_strings_in_file(file_path, redact_list):
    """
    Redact specified strings in a single file.
    
    Args:
        file_path (Path): Path to the file to process
        redact_list (list): List of strings to redact
    
    Returns:
        bool: True if file was modified, False otherwise
    """
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Redact each string in the list
        for string_to_redact in redact_list:
            if string_to_redact in content:
                # Replace with asterisks of the same length
                redacted = '*' * len(string_to_redact)
                content = content.replace(string_to_redact, redacted)
        
        # Write back only if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return False


def redact_directory(directory_path, redact_list):
    """
    Recursively traverse directory and redact strings in all text files.
    
    Args:
        directory_path (Path): Path to the directory to process
        redact_list (list): List of strings to redact
    """
    files_processed = 0
    files_modified = 0
    
    print(f"Starting redaction in directory: {directory_path}")
    print(f"Strings to redact: {redact_list}")
    print("-" * 50)
    
    # Walk through all files and subdirectories
    for root, dirs, files in os.walk(directory_path):
        for file_name in files:
            file_path = Path(root) / file_name
            
            # Skip if not a text file
            if not is_text_file(file_path):
                continue
            
            files_processed += 1
            print(f"Processing: {file_path}")
            
            if redact_strings_in_file(file_path, redact_list):
                files_modified += 1
                print(f"  ✓ Modified")
            else:
                print(f"  - No changes needed")
    
    print("-" * 50)
    print(f"Summary:")
    print(f"  Files processed: {files_processed}")
    print(f"  Files modified: {files_modified}")


def main():
    parser = argparse.ArgumentParser(
        description="Recursively redact specified strings from files in a directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python redact_names.py /path/to/files "John Doe" "Jane Smith"
  python redact_names.py ./documents "Bob" "Alice Johnson" "Company XYZ"
        """
    )
    
    parser.add_argument(
        'directory',
        help='Directory to process recursively'
    )
    
    parser.add_argument(
        'strings',
        nargs='+',
        help='Strings to redact (space-separated, use quotes for multi-word strings)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without actually modifying files'
    )
    
    args = parser.parse_args()
    
    # Validate directory exists
    directory_path = Path(args.directory)
    if not directory_path.exists():
        print(f"Error: Directory '{directory_path}' does not exist.")
        sys.exit(1)
    
    if not directory_path.is_dir():
        print(f"Error: '{directory_path}' is not a directory.")
        sys.exit(1)
    
    # Validate strings list
    if not args.strings:
        print("Error: At least one string to redact must be provided.")
        sys.exit(1)
    
    if args.dry_run:
        print("DRY RUN MODE - No files will be modified")
        print()
    
    # Perform redaction
    redact_directory(directory_path, args.strings)


if __name__ == "__main__":
    main()
