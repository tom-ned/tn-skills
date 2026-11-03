#!/usr/bin/env python3
"""
Extract HEADER + inline styles + CSS links from a client page.
Absolutise all relative URLs.

Usage: python extract_header.py https://www.client.com/example-product output_dir/
"""
import re, sys, os, urllib.request

def fetch(url):
    return urllib.request.urlopen(url, timeout=30).read().decode('utf-8', errors='replace')

def absolutize(s, base):
    return re.sub(r'(href|src|srcset)="(/[^"]*)"',
                  lambda m: f'{m.group(1)}="{base}{m.group(2)}"', s)

def main():
    if len(sys.argv) != 3:
        print("Usage: extract_header.py URL output_dir/")
        sys.exit(1)
    url, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    
    base = '/'.join(url.split('/')[:3])  # https://www.client.com
    html = fetch(url)
    
    # Extract pieces
    header_m = re.search(r'<header[^>]*>.*?</header>', html, re.DOTALL)
    if not header_m:
        print("No <header> tag found")
        sys.exit(1)
    header = absolutize(header_m.group(0), base)
    
    inline_styles = re.findall(r'<style[^>]*>.*?</style>', html, re.DOTALL)
    inline_styles_html = '\n'.join(inline_styles)
    
    css_links = re.findall(r'<link rel="stylesheet"[^>]+>', html)
    css_links_html = '\n'.join(absolutize(c, base) for c in css_links)
    
    with open(os.path.join(out_dir, 'header.html'), 'w', encoding='utf-8') as f:
        f.write(header)
    with open(os.path.join(out_dir, 'inline_styles.html'), 'w', encoding='utf-8') as f:
        f.write(inline_styles_html)
    with open(os.path.join(out_dir, 'css_links.html'), 'w', encoding='utf-8') as f:
        f.write(css_links_html)
    
    print(f"Header bytes: {len(header)}")
    print(f"Inline styles bytes: {len(inline_styles_html)}")
    print(f"CSS links: {len(css_links)}")
    print(f"Output: {out_dir}/")

if __name__ == '__main__':
    main()
