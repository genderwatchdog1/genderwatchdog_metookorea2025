#!/usr/bin/env python3
"""
Email Decoder Caller Script for Gender Watchdog Project

This script checks for .eml files in a source directory and calls decode_emails.py
for any files that don't have corresponding decoded files in the destination directory.

Usage:
    python decode_emails_caller.py <source_dir> <dest_dir>
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Check for .eml files and decode missing ones using decode_emails.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python decode_emails_caller.py email_emls/korean-press-gagged email_emls/decoded/korea-press-gagged
    python decode_emails_caller.py email_emls/korean-prosecutor-outreach email_emls/decoded/korean-prosecutor-outreach/
        """
    )
    
    parser.add_argument('source_dir', help='Source directory containing .eml files')
    parser.add_argument('dest_dir', help='Destination directory for decoded files')
    
    args = parser.parse_args()
    
    # Define source and destination directories from arguments
    src_dir = Path(args.source_dir)
    dest_dir = Path(args.dest_dir)
    
    # Check if source directory exists
    if not src_dir.exists():
        print(f"Error: Source directory '{src_dir}' does not exist")
        sys.exit(1)
    
    # Create destination directory if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"Source directory: {src_dir}")
    print(f"Destination directory: {dest_dir}")
    
    # Find all .eml files in source directory
    eml_files = list(src_dir.glob('*.eml'))
    
    if not eml_files:
        print(f"No .eml files found in '{src_dir}'")
        return
    
    print(f"Found {len(eml_files)} .eml files in source directory")
    
    # Check which files need to be decoded
    files_to_decode = []
    
    for eml_file in eml_files:
        # Expected decoded filename (decode_emails.py adds "decoded_" prefix)
        decoded_filename = f"decoded_{eml_file.name}"
        decoded_path = dest_dir / decoded_filename
        
        if not decoded_path.exists():
            files_to_decode.append(eml_file)
            print(f"  → {eml_file.name} needs decoding")
        else:
            print(f"  ✓ {eml_file.name} already decoded")
    
    if not files_to_decode:
        print("All .eml files have been decoded already")
        return
    
    print(f"\nDecoding {len(files_to_decode)} files...")
    
    # Process each file that needs decoding
    success_count = 0
    
    for eml_file in files_to_decode:
        try:
            # Call decode_emails.py for this specific file
            cmd = [
                sys.executable,  # Use the same Python interpreter
                "decode_emails.py",
                str(eml_file),
                str(dest_dir)
            ]
            
            print(f"\nProcessing: {eml_file.name}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                success_count += 1
                print(f"✓ Successfully decoded {eml_file.name}")
                if result.stdout:
                    print(result.stdout.strip())
            else:
                print(f"✗ Error decoding {eml_file.name}")
                if result.stderr:
                    print(f"Error: {result.stderr.strip()}")
                if result.stdout:
                    print(f"Output: {result.stdout.strip()}")
                    
        except Exception as e:
            print(f"✗ Failed to process {eml_file.name}: {e}")
    
    print(f"\n" + "="*60)
    print(f"Processing complete: {success_count}/{len(files_to_decode)} files decoded successfully")
    
    if success_count > 0:
        print(f"Decoded files saved to: {dest_dir}")


if __name__ == "__main__":
    main()
