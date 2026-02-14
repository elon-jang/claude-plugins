#!/usr/bin/env python3
"""
Fetch LinkedIn post content using Playwright headless browser.

Requires li_at cookie from linkedin_cookie.json.
Outputs JSON {title, author, content, url, published_date} to stdout.

Usage:
    python fetch_post.py "https://www.linkedin.com/posts/..." --verbose
    python fetch_post.py "https://www.linkedin.com/feed/update/..." --verbose
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Error: 'playwright' not found. Install with: pip install playwright && playwright install chromium", file=sys.stderr)
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: 'beautifulsoup4' not found. Install with: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

PROJECT_ROOT = Path(__file__).parent.parent

DEFAULT_COOKIE_PATH = Path.home() / "elon/ai/usecases/contents_hub/backend/data/linkedin_cookie.json"

# Tracking parameters to strip from URLs
TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "lipi", "lici", "rcm"}


def load_cookie(cookie_path: str | None = None) -> str:
    """Load li_at cookie from JSON file."""
    path = Path(cookie_path) if cookie_path else Path(os.getenv("LINKEDIN_COOKIE_PATH", str(DEFAULT_COOKIE_PATH)))

    if not path.exists():
        print(f"Error: Cookie file not found: {path}", file=sys.stderr)
        print("Set LINKEDIN_COOKIE_PATH or place cookie at default path.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(path.read_text())
    li_at = data.get("li_at")
    if not li_at:
        print("Error: 'li_at' key not found in cookie file.", file=sys.stderr)
        sys.exit(1)

    return li_at


def clean_url(url: str) -> str:
    """Remove tracking parameters from LinkedIn URL."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    cleaned = {k: v for k, v in params.items() if k not in TRACKING_PARAMS}
    new_query = urlencode(cleaned, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def validate_url(url: str) -> str:
    """Validate and normalize LinkedIn post URL."""
    parsed = urlparse(url)
    if "linkedin.com" not in parsed.netloc:
        print(f"Error: Not a LinkedIn URL: {url}", file=sys.stderr)
        sys.exit(1)

    path = parsed.path
    if not (path.startswith("/posts/") or path.startswith("/feed/update/")):
        # Check for profile-based post URL: /in/username/post/...
        if "/post/" not in path:
            print(f"Error: Not a LinkedIn post URL: {url}", file=sys.stderr)
            print("Supported: /posts/... or /feed/update/...", file=sys.stderr)
            sys.exit(1)

    return clean_url(url)


def fetch_post(url: str, li_at: str, verbose: bool = False) -> dict:
    """Fetch LinkedIn post content using Playwright."""
    if verbose:
        print(f"Fetching: {url}", file=sys.stderr)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 900},
        )

        context.add_cookies([{
            "name": "li_at",
            "value": li_at,
            "domain": ".linkedin.com",
            "path": "/",
        }])

        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)
        except Exception as e:
            browser.close()
            print(f"Error: Failed to load page: {e}", file=sys.stderr)
            sys.exit(1)

        html = page.content()
        title_tag = page.title()
        browser.close()

    if verbose:
        print(f"Page loaded. Title: {title_tag}", file=sys.stderr)

    soup = BeautifulSoup(html, "html.parser")

    # Extract post content
    content = extract_content(soup, verbose)
    if not content:
        print("Error: Could not extract post content. Cookie may be expired.", file=sys.stderr)
        sys.exit(1)

    # Extract author
    author = extract_author(soup, title_tag, url, verbose)

    # Extract published date
    published_date = extract_published_date(soup, verbose)

    # Generate title from content
    title = generate_title(content)

    return {
        "title": title,
        "author": author,
        "content": content,
        "url": url,
        "published_date": published_date,
    }


def extract_content(soup: BeautifulSoup, verbose: bool = False) -> str:
    """Extract post body text from parsed HTML."""
    selectors = [
        "span.break-words",
        "div.feed-shared-text",
        "span[dir='ltr']",
        "div.update-components-text",
        "div.feed-shared-update-v2__description",
    ]

    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            # Take the longest matching element (most likely the post body)
            texts = []
            for el in elements:
                text = el.get_text(separator="\n", strip=True)
                if text:
                    texts.append(text)

            if texts:
                best = max(texts, key=len)
                if len(best) > 30:
                    if verbose:
                        print(f"Content found via: {selector} ({len(best)} chars)", file=sys.stderr)
                    return best

    # Fallback: look for any substantial text block
    for tag in soup.find_all(["span", "div"], class_=re.compile(r"(text|content|body|description)", re.I)):
        text = tag.get_text(separator="\n", strip=True)
        if text and len(text) > 100:
            if verbose:
                print(f"Content found via fallback ({len(text)} chars)", file=sys.stderr)
            return text

    return ""


def extract_author(soup: BeautifulSoup, title_tag: str, url: str, verbose: bool = False) -> str:
    """Extract author name from parsed HTML."""
    # Try dedicated author element
    selectors = [
        "span.feed-shared-actor__name",
        "a.feed-shared-actor__container-link span",
        "span.update-components-actor__name",
        ".update-components-actor__title",
        "a.app-aware-link.update-components-actor__meta-link span",
        ".feed-shared-actor__title",
    ]

    for selector in selectors:
        el = soup.select_one(selector)
        if el:
            name = el.get_text(strip=True)
            if name and len(name) < 100:
                if verbose:
                    print(f"Author found via: {selector} → {name}", file=sys.stderr)
                return name

    # Try meta tags
    for meta_sel in ['meta[name="author"]', 'meta[property="article:author"]',
                     'meta[property="og:title"]']:
        meta = soup.select_one(meta_sel)
        if meta and meta.get("content"):
            content = meta["content"].strip()
            if meta_sel == 'meta[property="og:title"]':
                # Parse "Author on LinkedIn" or "Author Name | LinkedIn"
                m = re.match(r"^(.+?)\s+on\s+LinkedIn", content)
                if not m:
                    m = re.match(r"^(.+?)\s*[|\-]\s*LinkedIn", content)
                if m:
                    name = m.group(1).strip()
                    if name and len(name) < 100:
                        if verbose:
                            print(f"Author from og:title meta → {name}", file=sys.stderr)
                        return name
            else:
                if len(content) < 100:
                    if verbose:
                        print(f"Author from {meta_sel} → {content}", file=sys.stderr)
                    return content

    # Fallback: extract from <title> tag
    # Common format: "Author Name on LinkedIn: post text..."
    if title_tag:
        # Skip generic titles like "(8) Post | LinkedIn"
        if not re.match(r"^\(\d+\)\s+(Post|Feed)", title_tag):
            match = re.match(r"^(.+?)\s+on\s+LinkedIn", title_tag)
            if match:
                name = match.group(1).strip()
                if verbose:
                    print(f"Author from title tag → {name}", file=sys.stderr)
                return name

            # Korean LinkedIn: "Author Name | LinkedIn"
            match = re.match(r"^(.+?)\s*[|\-]\s*LinkedIn", title_tag)
            if match:
                name = match.group(1).strip()
                if verbose:
                    print(f"Author from title tag → {name}", file=sys.stderr)
                return name

            # Korean: "(숫자) 이름 님의 게시물 | LinkedIn"
            match = re.match(r"^\(\d+\)\s+(.+?)(?:\s*님의\s*게시물)", title_tag)
            if match:
                name = match.group(1).strip()
                if verbose:
                    print(f"Author from Korean title → {name}", file=sys.stderr)
                return name

    # Fallback: extract username from /posts/username_... URL
    parsed = urlparse(url)
    if parsed.path.startswith("/posts/"):
        slug = parsed.path.split("/posts/")[1]
        # URL format: /posts/username_slug-text-activity-...
        username = slug.split("_")[0]
        if username:
            if verbose:
                print(f"Author from URL slug → {username}", file=sys.stderr)
            return username

    return ""


def _parse_relative_time(text: str) -> str:
    """Parse relative time strings (English/Korean) to YYYY-MM-DD.

    Examples: "2w", "3d ago", "1mo", "2주 전", "3일", "1개월"
    Returns "" if no match.
    """
    text = text.strip().lower()
    now = datetime.now()

    # English patterns: "2w", "3d", "1mo", "5h", "3d ago", "1 week ago"
    en_match = re.match(r"(\d+)\s*(mo|w|d|h|m|yr|year|month|week|day|hour|min)", text)
    if en_match:
        num = int(en_match.group(1))
        unit = en_match.group(2)
        if unit in ("mo", "month"):
            delta = timedelta(days=num * 30)
        elif unit in ("w", "week"):
            delta = timedelta(weeks=num)
        elif unit in ("d", "day"):
            delta = timedelta(days=num)
        elif unit in ("h", "hour"):
            delta = timedelta(hours=num)
        elif unit in ("m", "min"):
            delta = timedelta(minutes=num)
        elif unit in ("yr", "year"):
            delta = timedelta(days=num * 365)
        else:
            return ""
        return (now - delta).strftime("%Y-%m-%d")

    # Korean patterns: "2주 전", "3일 전", "1개월 전", "5시간"
    ko_match = re.match(r"(\d+)\s*(개월|주|일|시간|분|년)", text)
    if ko_match:
        num = int(ko_match.group(1))
        unit = ko_match.group(2)
        if unit == "개월":
            delta = timedelta(days=num * 30)
        elif unit == "주":
            delta = timedelta(weeks=num)
        elif unit == "일":
            delta = timedelta(days=num)
        elif unit == "시간":
            delta = timedelta(hours=num)
        elif unit == "분":
            delta = timedelta(minutes=num)
        elif unit == "년":
            delta = timedelta(days=num * 365)
        else:
            return ""
        return (now - delta).strftime("%Y-%m-%d")

    return ""


def extract_published_date(soup: BeautifulSoup, verbose: bool = False) -> str:
    """Extract post published date from parsed HTML.

    Returns YYYY-MM-DD string or "" if not found.
    """
    # 1. <time datetime="..."> — ISO format, most accurate
    time_el = soup.find("time", attrs={"datetime": True})
    if time_el:
        dt_str = time_el["datetime"].strip()
        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            if verbose:
                print(f"Published date from <time> tag → {dt.strftime('%Y-%m-%d')}", file=sys.stderr)
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            pass

    # 2. Meta tags
    meta_selectors = [
        'meta[property="article:published_time"]',
        'meta[property="og:published_time"]',
        'meta[name="date"]',
    ]
    for sel in meta_selectors:
        meta = soup.select_one(sel)
        if meta and meta.get("content"):
            content = meta["content"].strip()
            try:
                dt = datetime.fromisoformat(content.replace("Z", "+00:00"))
                if verbose:
                    print(f"Published date from {sel} → {dt.strftime('%Y-%m-%d')}", file=sys.stderr)
                return dt.strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                pass

    # 3. Relative time selectors (LinkedIn-specific)
    relative_selectors = [
        "span.feed-shared-actor__sub-description",
        "span.update-components-actor__sub-description",
        ".feed-shared-actor__sub-description span",
        "a.app-aware-link span.visually-hidden",
    ]
    for sel in relative_selectors:
        elements = soup.select(sel)
        for el in elements:
            text = el.get_text(strip=True)
            if text and len(text) < 30:
                result = _parse_relative_time(text)
                if result:
                    if verbose:
                        print(f"Published date from relative time ({sel}: '{text}') → {result}", file=sys.stderr)
                    return result

    # 4. Fallback: scan all short <span> elements for relative time patterns
    for span in soup.find_all("span"):
        text = span.get_text(strip=True)
        if text and len(text) < 30:
            # Only try if it looks like a time string
            if re.search(r"\d+\s*(mo|w|d|h|m|yr|개월|주|일|시간|분|년)", text.lower()):
                result = _parse_relative_time(text)
                if result:
                    if verbose:
                        print(f"Published date from span fallback ('{text}') → {result}", file=sys.stderr)
                    return result

    if verbose:
        print("Published date: not found", file=sys.stderr)
    return ""


def generate_title(content: str) -> str:
    """Generate a short title from post content (first meaningful line, max 50 chars)."""
    lines = [line.strip() for line in content.split("\n") if line.strip()]
    if not lines:
        return "Untitled"

    first_line = lines[0]
    # Remove hashtags and special chars from beginning
    first_line = re.sub(r"^[#\s]+", "", first_line)

    if len(first_line) > 50:
        # Cut at word boundary
        truncated = first_line[:47]
        last_space = truncated.rfind(" ")
        if last_space > 20:
            truncated = truncated[:last_space]
        return truncated + "..."

    return first_line


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fetch LinkedIn post content")
    parser.add_argument("url", help="LinkedIn post URL")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show progress on stderr")
    parser.add_argument("--cookie", type=str, help="Path to linkedin_cookie.json")

    args = parser.parse_args()

    url = validate_url(args.url)
    li_at = load_cookie(args.cookie)
    result = fetch_post(url, li_at, verbose=args.verbose)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
