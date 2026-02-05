#!/usr/bin/env python3
"""
URL Shortener for LinkedIn posts using Bitly API.

Finds all URLs in a given text or markdown file and shortens them.
Skips already-short URLs (bit.ly, lnkd.in, youtu.be, t.co, etc.).
Requires BITLY_TOKEN in environment variables or .env file.

Usage:
    python shorten_urls.py "Your text with https://example.com/long/url"
    python shorten_urls.py --file data/posts/my-post.md
    python shorten_urls.py --verbose "Text here"
"""

import os
import re
import sys
import json
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Warning: 'python-dotenv' not found. Install with: pip install python-dotenv", file=sys.stderr)
    load_dotenv = lambda *a, **kw: None

PROJECT_ROOT = Path(__file__).parent.parent

# URL regex pattern
URL_PATTERN = r'https?://[^\s<>"\'\)\]]+'

# Bitly API endpoint
BITLY_API_URL = "https://api-ssl.bitly.com/v4/shorten"

# Domains that are already short — skip these
SHORT_DOMAINS = {
    "bit.ly", "lnkd.in", "youtu.be", "t.co", "goo.gl",
    "tinyurl.com", "ow.ly", "is.gd", "buff.ly", "adf.ly",
    "amzn.to", "rb.gy", "shorturl.at",
}


def load_bitly_token():
    """Load Bitly API token from environment or .env file."""
    env_path = PROJECT_ROOT / ".env"
    load_dotenv(env_path)

    token = os.getenv("BITLY_TOKEN")
    if not token:
        print("Error: BITLY_TOKEN not found.", file=sys.stderr)
        print("Add BITLY_TOKEN=your_token to .env", file=sys.stderr)
        sys.exit(1)

    return token


def is_short_url(url: str) -> bool:
    """Check if a URL is already shortened."""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        return domain in SHORT_DOMAINS
    except Exception:
        return False


def shorten_url(url: str, token: str) -> str | None:
    """Shorten a single URL using Bitly API."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {"long_url": url}

    try:
        response = requests.post(BITLY_API_URL, headers=headers, json=data, timeout=10)

        if response.status_code in [200, 201]:
            return response.json().get("link")
        elif response.status_code == 403:
            print("Error: Invalid BITLY_TOKEN or insufficient permissions", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"Warning: Failed to shorten '{url}': HTTP {response.status_code}", file=sys.stderr)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Warning: Network error shortening '{url}': {e}", file=sys.stderr)
        return None


def shorten_urls_in_text(text: str, token: str, verbose: bool = False, skip_short: bool = True) -> tuple[str, dict]:
    """
    Find and shorten all URLs in text.

    Args:
        text: Input text containing URLs
        token: Bitly API token
        verbose: Print detailed info
        skip_short: Skip already-short URLs

    Returns:
        (modified_text, url_mapping)
    """
    urls = re.findall(URL_PATTERN, text)

    if not urls:
        if verbose:
            print("No URLs found.", file=sys.stderr)
        return text, {}

    # Deduplicate while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    if verbose:
        print(f"Found {len(unique_urls)} unique URL(s).", file=sys.stderr)

    url_mapping = {}
    modified_text = text

    for url in unique_urls:
        if skip_short and is_short_url(url):
            if verbose:
                print(f"  Skip (already short): {url}", file=sys.stderr)
            continue

        if verbose:
            print(f"  Shortening: {url}", file=sys.stderr)

        shortened = shorten_url(url, token)

        if shortened:
            url_mapping[url] = shortened
            modified_text = modified_text.replace(url, shortened)
            if verbose:
                print(f"    → {shortened}", file=sys.stderr)
        else:
            if verbose:
                print(f"    → Kept original", file=sys.stderr)

    return modified_text, url_mapping


def shorten_file(file_path: Path, token: str, verbose: bool = False, dry_run: bool = False) -> dict:
    """
    Shorten URLs in a markdown file (with frontmatter).

    Args:
        file_path: Path to markdown file
        token: Bitly API token
        verbose: Print detailed info
        dry_run: Don't write changes

    Returns:
        url_mapping dict
    """
    try:
        import frontmatter
    except ImportError:
        print("Error: 'python-frontmatter' not found. Install with: pip install python-frontmatter", file=sys.stderr)
        sys.exit(1)

    post = frontmatter.load(file_path)

    # Shorten URLs in body
    modified_body, body_mapping = shorten_urls_in_text(post.content, token, verbose=verbose)

    # Shorten frontmatter url field
    fm_mapping = {}
    url_field = post.get("url", "")
    if url_field and not is_short_url(url_field):
        shortened = shorten_url(url_field, token)
        if shortened:
            fm_mapping[url_field] = shortened
            post["url"] = shortened
            if verbose:
                print(f"  Frontmatter url: {url_field} → {shortened}", file=sys.stderr)

    post.content = modified_body
    all_mapping = {**body_mapping, **fm_mapping}

    if all_mapping and not dry_run:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))
        if verbose:
            print(f"  Saved: {file_path}", file=sys.stderr)
    elif not all_mapping:
        if verbose:
            print(f"  No URLs to shorten in {file_path.name}", file=sys.stderr)

    return all_mapping


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Shorten URLs using Bitly API")
    parser.add_argument("text", nargs="*", help="Text containing URLs to shorten")
    parser.add_argument("--file", "-f", type=str, help="Markdown file to process")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing (--file mode)")
    parser.add_argument("--no-skip-short", action="store_true", help="Don't skip already-short URLs")

    args = parser.parse_args()

    token = load_bitly_token()
    skip_short = not args.no_skip_short

    if args.file:
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = PROJECT_ROOT / file_path
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)

        mapping = shorten_file(file_path, token, verbose=args.verbose, dry_run=args.dry_run)
        if mapping:
            print(json.dumps(mapping, indent=2))
        else:
            print("No URLs shortened.")
    elif args.text:
        text = " ".join(args.text)
        modified, mapping = shorten_urls_in_text(text, token, verbose=args.verbose, skip_short=skip_short)
        print(modified)
        if args.verbose and mapping:
            print("\nURL Mapping:", file=sys.stderr)
            print(json.dumps(mapping, indent=2), file=sys.stderr)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
