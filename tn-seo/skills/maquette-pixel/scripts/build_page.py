#!/usr/bin/env python3
"""
Assemble a Suisseo maquette : client header (extracted) + Suisseo body + Suisseo footer + overlay.

Usage : python build_page.py CONFIG.json output.html
CONFIG.json schema (see config_example.json next to this script).
"""
import json, sys, os, re

def read(p):
    with open(p, encoding='utf-8') as f: return f.read()

def main():
    if len(sys.argv) != 3:
        print("Usage: build_page.py CONFIG.json output.html"); sys.exit(1)
    cfg = json.loads(read(sys.argv[1]))
    out = sys.argv[2]
    
    here = os.path.dirname(os.path.abspath(__file__))
    tpl_dir = os.path.join(os.path.dirname(here), 'templates')
    
    head_tpl = read(os.path.join(tpl_dir, 'head_template.html'))
    body_tpl = read(os.path.join(tpl_dir, 'body_template.html'))
    footer_tpl = read(os.path.join(tpl_dir, 'footer_suisseo.html'))
    
    # Read extracted client pieces
    extracted = cfg.get('extracted_dir', '.')
    client_header = read(os.path.join(extracted, 'header.html'))
    client_inline = read(os.path.join(extracted, 'inline_styles.html'))
    client_css = read(os.path.join(extracted, 'css_links.html'))
    
    # Replace head placeholders
    head = head_tpl
    head_subs = {
        '[LANG]': cfg.get('lang', 'en'),
        '[TITLE_50_65_CHAR_WITH_TARGET_KW]': cfg['title'],
        '[META_DESC_145_160_CHAR]': cfg['meta_description'],
        '[CANONICAL_URL]': cfg['canonical_url'],
        '[OG_TITLE]': cfg.get('og_title', cfg['title']),
        '[OG_DESC]': cfg.get('og_description', cfg['meta_description']),
        '[OG_IMAGE_URL]': cfg['og_image_url'],
        '[FAVICON_URL]': cfg.get('favicon_url', ''),
        '[CLIENT_DOMAIN]': cfg['client_domain'],
        '[CLIENT_INLINE_STYLES]': client_inline,
        '[CLIENT_CSS_LINKS]': client_css,
        '[SCHEMA_TYPE]': cfg.get('schema_type', 'Service'),
        '[SCHEMA_NAME]': cfg.get('schema_name', cfg['title']),
        '[SCHEMA_DESC]': cfg.get('schema_desc', cfg['meta_description']),
        '[CLIENT_HEADER_HTML]': client_header,
        '[BODY_CONTENT]': body_tpl,
        '[FOOTER_SUISSEO_HTML]': footer_tpl,
        '[PAGE_LABEL]': cfg.get('page_label', 'Demo'),
    }
    for k, v in head_subs.items():
        head = head.replace(k, v)
    
    # Replace body placeholders from cfg.body
    for k, v in cfg.get('body', {}).items():
        head = head.replace(f'[{k}]', v)
    
    # Replace footer placeholders from cfg.footer
    for k, v in cfg.get('footer', {}).items():
        head = head.replace(f'[{k}]', v)
    
    with open(out, 'w', encoding='utf-8') as f: f.write(head)
    print(f"Page built: {out} ({os.path.getsize(out)} bytes)")

if __name__ == '__main__':
    main()
