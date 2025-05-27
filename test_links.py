import os
import re
import sys
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# List of HTML files to check (default in root directory)
HTML_FILES = [
    'index.html',
    'timeline_ko.html',
    'timeline_ja.html',
    'timeline_zh_cn.html',
    'timeline_zh_tw.html',
]

# Regex for blog links
BLOG_LINK_RE = re.compile(r'https://blog\.genderwatchdog\.org/[^\s"\']+')


def check_html_file(filepath):
    print(f'Checking {filepath}...')
    try:
        with open(filepath, encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f'  ERROR: Could not read {filepath}: {e}')
        return False, []
    try:
        soup = BeautifulSoup(html, 'html.parser')
    except Exception as e:
        print(f'  ERROR: Could not parse {filepath}: {e}')
        return False, []
    
    # Find all links in the document
    external_links = []
    internal_links = []
    special_links = []  # For mailto, tel, etc.
    
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        
        # Skip empty links, javascript links, and anchor links
        if not href or href.startswith('javascript:') or href == '#' or href.startswith('#'):
            continue
        
        # Check for special protocol links (mailto, tel, etc.)
        if href.startswith('mailto:') or href.startswith('tel:'):
            link_text = a.get_text(strip=True) or "[No text]"
            special_links.append((href, link_text))
            continue
            
        # Check if it's an external link
        if href.startswith('http://') or href.startswith('https://'):
            external_links.append(href)
        else:
            # It's a relative link - capture link text for better reporting
            link_text = a.get_text(strip=True) or "[No text]"
            internal_links.append((href, link_text))
    
    print(f'  Found {len(external_links)} external links, {len(internal_links)} internal links, and {len(special_links)} special links.')
    return True, (external_links, internal_links, special_links, filepath)


def check_external_link(url):
    """Verify external URL by making a HEAD request"""
    try:
        resp = requests.head(url, allow_redirects=True, timeout=10)
        if resp.status_code == 200:
            return True, None
        # Some sites don't accept HEAD requests, try GET if HEAD fails
        elif resp.status_code == 405:  # Method Not Allowed
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    return True, None
                else:
                    error_msg = f'Status {resp.status_code}'
                    print(f'    BAD LINK: {url} ({error_msg})')
                    return False, error_msg
            except Exception as e:
                error_msg = f'GET request failed: {e}'
                print(f'    ERROR: {error_msg} for {url}')
                return False, error_msg
        else:
            error_msg = f'Status {resp.status_code}'
            print(f'    BAD LINK: {url} ({error_msg})')
            return False, error_msg
    except Exception as e:
        error_msg = f'Connection error: {e}'
        print(f'    ERROR: Could not reach {url}: {e}')
        return False, error_msg


def check_internal_link(link_info, base_file):
    """Verify internal link by checking if the file exists on disk"""
    link, link_text = link_info
    # Get the directory of the current HTML file
    base_dir = os.path.dirname(os.path.abspath(base_file))
    
    # Handle different types of relative paths
    if link.startswith('/'):
        # Absolute path from project root
        target_path = os.path.join(os.getcwd(), link.lstrip('/'))
    else:
        # Relative path from current file
        target_path = os.path.normpath(os.path.join(base_dir, link))
    
    # If link contains an anchor (#), strip it off for file existence check
    if '#' in target_path:
        target_path = target_path.split('#')[0]
        
    # If link is empty after stripping anchor, it's a self-reference
    if not target_path:
        return True, None
        
    # If it ends with /, assume it's a directory and check for its existence
    if target_path.endswith('/'):
        exists = os.path.isdir(target_path)
        if not exists:
            error_msg = f'Directory not found at {target_path}'
            print(f'    BAD LINK: "{link}" → "{link_text}" ({error_msg})')
            return False, error_msg
        return True, None
    
    # Check if file exists
    exists = os.path.exists(target_path)
    if not exists:
        error_msg = f'File not found at {target_path}'
        print(f'    BAD LINK: "{link}" → "{link_text}" ({error_msg})')
        return False, error_msg
    return True, None


def check_special_link(link_info):
    """Verify special links like mailto: and tel:"""
    href, link_text = link_info
    
    # For mailto links, just check basic format
    if href.startswith('mailto:'):
        email = href[7:]  # Remove 'mailto:' prefix
        # Very basic email validation
        if '@' in email and '.' in email.split('@')[1]:
            return True, None
        else:
            error_msg = 'Invalid email format'
            print(f'    BAD LINK: "{href}" → "{link_text}" ({error_msg})')
            return False, error_msg
    
    # For tel links, just check if it contains digits
    elif href.startswith('tel:'):
        phone = href[4:]  # Remove 'tel:' prefix
        if any(char.isdigit() for char in phone):
            return True, None
        else:
            error_msg = 'Invalid phone format'
            print(f'    BAD LINK: "{href}" → "{link_text}" ({error_msg})')
            return False, error_msg
    
    # Other special protocols - assume valid
    return True, None


def find_html_files(directory):
    """Recursively find all HTML files in a directory"""
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files


def main():
    # Check if a specific file or directory was provided as a command-line argument
    files_to_check = []
    
    if len(sys.argv) > 1:
        path_param = sys.argv[1]
        
        if os.path.isfile(path_param):
            # Single file mode
            if path_param.lower().endswith('.html'):
                files_to_check = [path_param]
            else:
                print(f"Error: File '{path_param}' is not an HTML file.")
                return
        elif os.path.isdir(path_param):
            # Directory mode - scan recursively
            print(f"Scanning directory '{path_param}' for HTML files...")
            files_to_check = find_html_files(path_param)
            print(f"Found {len(files_to_check)} HTML files to check.")
        else:
            print(f"Error: Path '{path_param}' not found.")
            return
    else:
        # Default mode - check predefined files and also scan all directories
        print("No path specified. Checking default files and scanning all directories recursively...")
        files_to_check = HTML_FILES.copy()
        html_in_dirs = find_html_files('.')
        
        # Only add files that aren't already in the default list
        for html_file in html_in_dirs:
            if html_file not in files_to_check and os.path.normpath(html_file) not in files_to_check:
                files_to_check.append(html_file)
        
        print(f"Found {len(files_to_check)} HTML files to check.")
    
    all_passed = True
    file_count = 0
    external_links_count = 0
    internal_links_count = 0
    special_links_count = 0
    broken_external_links = 0
    broken_internal_links = 0
    broken_special_links = 0
    
    # Track broken links for summary
    broken_links_summary = {}
    
    print("\n=== Checking HTML files ===\n")
    
    for html_file in files_to_check:
        if not os.path.exists(html_file):
            print(f'File not found: {html_file}')
            all_passed = False
            continue
        
        file_count += 1
        ok, link_data = check_html_file(html_file)
        if not ok:
            all_passed = False
            continue
        
        # Create an entry for this file in the broken links summary
        broken_links_summary[html_file] = []
        
        external_links, internal_links, special_links, base_file = link_data
        external_links_count += len(external_links)
        internal_links_count += len(internal_links)
        special_links_count += len(special_links)
        
        # Check external links
        if external_links:
            print(f"  Checking {len(external_links)} external links...")
            for link in external_links:
                ok, error = check_external_link(link)
                if not ok:
                    broken_external_links += 1
                    broken_links_summary[html_file].append((link, "External", error))
                    all_passed = False
        
        # Check internal links
        if internal_links:
            print(f"  Checking {len(internal_links)} internal links...")
            for link_info in internal_links:
                link, link_text = link_info
                ok, error = check_internal_link(link_info, base_file)
                if not ok:
                    broken_internal_links += 1
                    broken_links_summary[html_file].append((link, "Internal", error))
                    all_passed = False
        
        # Check special links (mailto, tel, etc.)
        if special_links:
            print(f"  Checking {len(special_links)} special links (mailto, tel, etc.)...")
            for link_info in special_links:
                href, link_text = link_info
                ok, error = check_special_link(link_info)
                if not ok:
                    broken_special_links += 1
                    broken_links_summary[html_file].append((href, "Special", error))
                    all_passed = False
        
        # Remove files with no broken links from the summary
        if not broken_links_summary[html_file]:
            del broken_links_summary[html_file]
    
    print("\n=== Summary ===")
    print(f"Checked {file_count} HTML files")
    print(f"Found {external_links_count} external links ({broken_external_links} broken)")
    print(f"Found {internal_links_count} internal links ({broken_internal_links} broken)")
    print(f"Found {special_links_count} special links ({broken_special_links} broken)")
    
    total_broken = broken_external_links + broken_internal_links + broken_special_links
    
    if all_passed:
        print("\n✅ All links are valid!")
    else:
        print(f"\n❌ Found {total_broken} broken links.")
        
        # Print the broken links summary
        print("\n=== Broken Links Details ===")
        for file_path, broken_links in broken_links_summary.items():
            if broken_links:
                print(f"\n📄 {file_path}")
                for link, link_type, error in broken_links:
                    print(f"  • [{link_type}] {link} - {error}")
        
    print("\nNOTE: Relative links are verified by checking if the file exists on your local filesystem.")
    print("      This script does NOT make HTTP requests for relative links - it only confirms the files exist.")
    print("      Special links like mailto: are validated for basic format only.")
    print("      Be sure that your production server structure matches your local development environment.")


if __name__ == '__main__':
    main() 