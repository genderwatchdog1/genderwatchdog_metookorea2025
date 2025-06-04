#!/usr/bin/env python3
"""
Email Decoder Script for Gender Watchdog Project

This script decodes .eml files by extracting and decoding their base64-encoded content.
It supports both single file processing and batch processing of entire directories.

Usage:
    python decode_emails.py <input_path> [output_dir]
    
    input_path: Path to a single .eml file or directory containing .eml files
    output_dir: Output directory (default: email_emls/decoded)
"""

import os
import sys
import argparse
import base64
import email
import quopri
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import html


def decode_base64_content(content):
    """Decode base64 encoded content."""
    try:
        decoded_bytes = base64.b64decode(content)
        # Try different encodings
        for encoding in ['utf-8', 'utf-16', 'latin-1', 'cp1252']:
            try:
                return decoded_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        # If all encodings fail, return with error replacement
        return decoded_bytes.decode('utf-8', errors='replace')
    except Exception as e:
        return f"[Error decoding base64: {e}]"


def decode_quoted_printable(content):
    """Decode quoted-printable encoded content."""
    try:
        decoded_bytes = quopri.decodestring(content.encode())
        return decoded_bytes.decode('utf-8', errors='replace')
    except Exception as e:
        return f"[Error decoding quoted-printable: {e}]"


def extract_text_from_html(html_content):
    """Extract readable text from HTML content."""
    try:
        # Simple HTML tag removal - could be enhanced with BeautifulSoup if needed
        import re
        # Remove script and style elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        
        # Replace common HTML entities
        html_content = html.unescape(html_content)
        
        # Replace HTML tags with appropriate text
        html_content = re.sub(r'<br[^>]*>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<p[^>]*>', '\n\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</p>', '', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<div[^>]*>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'</div>', '', html_content, flags=re.IGNORECASE)
        
        # Remove all remaining HTML tags
        html_content = re.sub(r'<[^>]+>', '', html_content)
        
        # Clean up whitespace
        html_content = re.sub(r'\n\s*\n', '\n\n', html_content)
        html_content = html_content.strip()
        
        return html_content
    except Exception as e:
        return f"[Error extracting text from HTML: {e}]\n\n{html_content}"


def decode_email_file(input_path, output_path):
    """Decode a single .eml file."""
    try:
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            email_content = f.read()
        
        # Parse the email
        msg = email.message_from_string(email_content)
        
        # Extract headers
        decoded_content = []
        decoded_content.append("=" * 80)
        decoded_content.append("EMAIL HEADERS")
        decoded_content.append("=" * 80)
        
        important_headers = [
            'From', 'To', 'Cc', 'Bcc', 'Subject', 'Date', 
            'Message-ID', 'In-Reply-To', 'References'
        ]
        
        for header in important_headers:
            if msg.get(header):
                decoded_content.append(f"{header}: {msg.get(header)}")
        
        decoded_content.append("\n" + "=" * 80)
        decoded_content.append("EMAIL CONTENT")
        decoded_content.append("=" * 80 + "\n")
        
        # Process email parts
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition', ''))
                
                # Skip attachments
                if 'attachment' in content_disposition:
                    decoded_content.append(f"[ATTACHMENT: {part.get_filename() or 'unnamed'}]")
                    continue
                
                if content_type in ['text/plain', 'text/html']:
                    payload = part.get_payload()
                    encoding = part.get('Content-Transfer-Encoding', '').lower()
                    
                    if encoding == 'base64':
                        decoded_text = decode_base64_content(payload)
                    elif encoding == 'quoted-printable':
                        decoded_text = decode_quoted_printable(payload)
                    else:
                        decoded_text = payload
                    
                    if content_type == 'text/html':
                        decoded_text = extract_text_from_html(decoded_text)
                        decoded_content.append("--- HTML CONTENT (converted to text) ---")
                    else:
                        decoded_content.append("--- PLAIN TEXT CONTENT ---")
                    
                    decoded_content.append(decoded_text)
                    decoded_content.append("")
        else:
            # Single part message
            payload = msg.get_payload()
            encoding = msg.get('Content-Transfer-Encoding', '').lower()
            content_type = msg.get_content_type()
            
            if encoding == 'base64':
                decoded_text = decode_base64_content(payload)
            elif encoding == 'quoted-printable':
                decoded_text = decode_quoted_printable(payload)
            else:
                decoded_text = payload
            
            if content_type == 'text/html':
                decoded_text = extract_text_from_html(decoded_text)
                decoded_content.append("--- HTML CONTENT (converted to text) ---")
            else:
                decoded_content.append("--- PLAIN TEXT CONTENT ---")
            
            decoded_content.append(decoded_text)
        
        # Write decoded content
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(decoded_content))
        
        print(f"✓ Decoded: {input_path} -> {output_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error decoding {input_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Decode .eml files by extracting and decoding their content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python decode_emails.py email.eml
    python decode_emails.py email.eml custom_output/
    python decode_emails.py email_emls/
    python decode_emails.py email_emls/ decoded_emails/
        """
    )
    
    parser.add_argument('input_path', help='Path to .eml file or directory containing .eml files')
    parser.add_argument('output_dir', nargs='?', default='email_emls/decoded', 
                       help='Output directory (default: email_emls/decoded)')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_path)
    output_dir = Path(args.output_dir)
    
    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist")
        sys.exit(1)
    
    success_count = 0
    total_count = 0
    
    if input_path.is_file():
        # Single file processing
        if not input_path.suffix.lower() == '.eml':
            print(f"Error: '{input_path}' is not a .eml file")
            sys.exit(1)
        
        output_filename = f"decoded_{input_path.name}"
        output_path = output_dir / output_filename
        
        total_count = 1
        if decode_email_file(input_path, output_path):
            success_count = 1
            
    elif input_path.is_dir():
        # Directory processing
        eml_files = list(input_path.glob('*.eml'))
        
        if not eml_files:
            print(f"No .eml files found in '{input_path}'")
            sys.exit(1)
        
        print(f"Found {len(eml_files)} .eml files to process...")
        
        for eml_file in eml_files:
            output_filename = f"decoded_{eml_file.name}"
            output_path = output_dir / output_filename
            
            total_count += 1
            if decode_email_file(eml_file, output_path):
                success_count += 1
    else:
        print(f"Error: '{input_path}' is neither a file nor a directory")
        sys.exit(1)
    
    print(f"\nProcessing complete: {success_count}/{total_count} files decoded successfully")
    
    if success_count > 0:
        print(f"Decoded files saved to: {output_dir}")


if __name__ == "__main__":
    main()
