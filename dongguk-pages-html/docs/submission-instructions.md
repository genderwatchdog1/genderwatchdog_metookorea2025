# Search Engine Submission Instructions

This document provides instructions for submitting and verifying the genderwatchdog.org domain and its subdomains to various search engines.

## Google Search Console

1. Go to [Google Search Console](https://search.google.com/search-console)
2. Add the following properties:
   - `https://genderwatchdog.org/` (main domain)
   - Future: Add other subdomains as they are developed
3. Verify ownership via one of these methods:
   - HTML file upload (use the template in `seo/google-site-verification.html` and update the content attribute)
   - DNS verification (preferred method - add the TXT record provided by Google to your DNS settings)
4. Submit sitemaps:
   - Go to "Sitemaps" section in Search Console
   - Enter `sitemap.xml` and click Submit
   - Verify the sitemap is being processed without errors

## Bing Webmaster Tools

1. Go to [Bing Webmaster Tools](https://www.bing.com/webmasters/about)
2. Add your site: `https://genderwatchdog.org/`
3. Verify ownership using one of the following methods:
   - XML file upload
   - Meta tag verification
   - DNS verification (recommended)
4. Submit your sitemap in the Sitemaps section

## Yandex Webmaster

1. Go to [Yandex Webmaster](https://webmaster.yandex.com/welcome/)
2. Add site: `https://genderwatchdog.org/`
3. Verify ownership
4. Submit sitemap

## Baidu (for Chinese language content once created)

1. Create a Baidu account at [Baidu Webmaster Tools](https://ziyuan.baidu.com/)
2. Add site: `https://genderwatchdog.org/`
3. Verify ownership with one of their provided methods
4. Submit sitemap

## Note regarding Naver

Currently, Naver submission is not possible as it requires a Korean phone number or ID for verification, which would break anonymity. If this requirement changes in the future or if anonymity is no longer a concern, follow these steps:

1. Go to [Naver Webmaster Tools](https://webmastertool.naver.com/)
2. Register and verify the site
3. Submit the Korean language sitemap

## Important SEO Files

- `sitemap.xml` - Contains links to all pages
- `robots.txt` - Directs search engines on what to crawl
- Canonical and hreflang tags - Added to HTML pages to properly identify language versions

## Regular Monitoring

After submission, regularly check:

1. Google Search Console for:
   - Indexing status
   - Search performance
   - Mobile usability issues
   - Core Web Vitals
   - Any reported errors

2. Bing Webmaster Tools for:
   - Crawl errors
   - Keyword performance
   - SEO suggestions

## Re-submission Schedule

- Re-submit sitemaps monthly, especially after adding new content
- Check search console dashboards weekly for issues 