#!/usr/bin/env python3
"""
Sitemap Generator for genderwatchdog.org

This script crawls the website and generates a sitemap.xml file
with proper lastmod dates and alternate language links.

Usage:
    python3 generate_sitemap.py

Requirements:
    - requests
    - beautifulsoup4
    - lxml

Install with: pip install requests beautifulsoup4 lxml
"""

import os
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import xml.dom.minidom

# Configuration
BASE_URL = "https://genderwatchdog.org"
OUTPUT_FILE = "../sitemap.xml"
FREQ = "weekly"
PRIORITY = {
    "": 1.0,  # Korean homepage
    "index-en.html": 0.9,  # English homepage
    # Add more priorities for other pages as needed
}
LANGUAGES = ["ko", "en"]  # Add more as they are developed
LANGUAGE_MAPPINGS = {
    "": "ko",  # Root path is Korean
    "index-en.html": "en"
}
IGNORED_EXTENSIONS = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']

def get_all_pages(base_url):
    """Crawl the website and get all pages."""
    pages = set()
    pages_to_check = [base_url]
    checked_pages = set()
    
    print(f"Crawling {base_url} to find all pages...")
    
    while pages_to_check:
        url = pages_to_check.pop(0)
        if url in checked_pages:
            continue
            
        checked_pages.add(url)
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch {url}: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Add this page to our set
            relative_url = url.replace(base_url, '')
            if not relative_url:
                relative_url = ""  # Root page
            pages.add(relative_url)
            
            # Find all links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if href.startswith('#') or any(href.endswith(ext) for ext in IGNORED_EXTENSIONS):
                    continue
                    
                full_url = urljoin(url, href)
                # Only include URLs from our domain
                if BASE_URL in full_url and full_url not in checked_pages and full_url not in pages_to_check:
                    pages_to_check.append(full_url)
                    
        except Exception as e:
            print(f"Error processing {url}: {e}")
    
    return pages

def create_sitemap(pages):
    """Create the sitemap XML."""
    impl = xml.dom.minidom.getDOMImplementation()
    doc = impl.createDocument(None, "urlset", None)
    root = doc.documentElement
    root.setAttribute("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    root.setAttribute("xmlns:xhtml", "http://www.w3.org/1999/xhtml")
    
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")
    
    for page in sorted(pages):
        url_element = doc.createElement("url")
        
        # Add loc element
        loc = doc.createElement("loc")
        loc_text = doc.createTextNode(urljoin(BASE_URL, page))
        loc.appendChild(loc_text)
        url_element.appendChild(loc)
        
        # Add lastmod element
        lastmod = doc.createElement("lastmod")
        lastmod_text = doc.createTextNode(now)
        lastmod.appendChild(lastmod_text)
        url_element.appendChild(lastmod)
        
        # Add changefreq element
        changefreq = doc.createElement("changefreq")
        changefreq_text = doc.createTextNode(FREQ)
        changefreq.appendChild(changefreq_text)
        url_element.appendChild(changefreq)
        
        # Add priority element
        priority_value = PRIORITY.get(page, 0.8)  # Default priority is 0.8
        priority = doc.createElement("priority")
        priority_text = doc.createTextNode(str(priority_value))
        priority.appendChild(priority_text)
        url_element.appendChild(priority)
        
        # Add alternate language links
        current_lang = LANGUAGE_MAPPINGS.get(page, "")
        if current_lang:
            for lang in LANGUAGES:
                # Skip if it's the same language
                lang_page = page
                if lang != current_lang:
                    # Get corresponding page for this language
                    if lang == "ko" and page != "":
                        lang_page = ""  # Root for Korean
                    elif lang == "en" and page == "":
                        lang_page = "index-en.html"  # English page
                    # Add more mappings as needed
                
                link = doc.createElement("xhtml:link")
                link.setAttribute("rel", "alternate")
                link.setAttribute("hreflang", lang)
                link.setAttribute("href", urljoin(BASE_URL, lang_page))
                url_element.appendChild(link)
        
        root.appendChild(url_element)
    
    return doc.toprettyxml(indent="  ")

def main():
    """Main function."""
    pages = get_all_pages(BASE_URL)
    sitemap_xml = create_sitemap(pages)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(sitemap_xml)
    
    print(f"Sitemap generated at {OUTPUT_FILE} with {len(pages)} URLs")

if __name__ == "__main__":
    main() 