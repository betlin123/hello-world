#!/usr/bin/env python3
"""Watch a public Facebook page for new posts and email you when one appears.

Uses only the Python standard library: fetches the mobile page
(m.facebook.com) without logging in, extracts post permalinks, and diffs
them against a local state file to find anything new.

Facebook does not offer a public, no-login API for arbitrary Pages, and it
frequently changes its HTML and rate-limits/blocks automated requests. This
script is a best-effort scraper: it detects common "please log in" walls and
reports them clearly instead of silently failing. You may need to adjust the
regex patterns in extract_posts() if Facebook changes its markup.

Usage:
    python3 facebook_page_watcher.py --to you@example.com

Email sending uses Gmail SMTP with an App Password (not your normal Gmail
password). Set these environment variables first:
    export GMAIL_USER="you@gmail.com"
    export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"

Create an App Password at https://myaccount.google.com/apppasswords
(requires 2-Step Verification enabled on the Google account).

Run it periodically with cron, e.g. every 30 minutes:
    */30 * * * * cd /path/to/repo && /usr/bin/python3 facebook_page_watcher.py --to you@example.com >> watcher.log 2>&1
"""

import argparse
import html
import json
import os
import re
import smtplib
import sys
import urllib.error
import urllib.request
from email.mime.text import MIMEText

DEFAULT_PAGE_URL = "https://m.facebook.com/Asukaspuistofyyri/"
DEFAULT_STATE_FILE = "facebook_watcher_state.json"

USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
)

LOGIN_WALL_SIGNALS = (
    "log in to continue",
    "you must log in",
    "login.php",
    "log_in.php",
    'name="login"',
    "you must log into facebook",
)

POST_LINK_PATTERN = re.compile(
    r'href="(/(?:story\.php\?story_fbid=[^"&]+[^"]*'
    r"|permalink\.php\?story_fbid=[^\"&]+[^\"]*"
    r'|[^/"]+/posts/[^"]+))"'
)

TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")


def fetch_page(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"could not fetch {url}: {exc}") from exc


def looks_like_login_wall(html: str) -> bool:
    lowered = html.lower()
    return any(signal in lowered for signal in LOGIN_WALL_SIGNALS)


def strip_tags(fragment: str) -> str:
    text = TAG_PATTERN.sub(" ", fragment)
    text = WHITESPACE_PATTERN.sub(" ", text).strip()
    return text


def normalize_post_url(base_url: str, href: str) -> str:
    href = html.unescape(href)
    if href.startswith("http"):
        return href
    origin = "https://m.facebook.com"
    return origin + href


def extract_posts(html: str, page_url: str, snippet_window: int = 300):
    posts = []
    seen_urls = set()
    for match in POST_LINK_PATTERN.finditer(html):
        href = match.group(1)
        url = normalize_post_url(page_url, href)
        # Strip tracking params that change on every fetch so the same post
        # doesn't look "new" every run.
        url = url.split("&refid=")[0].split("?__tn__")[0]
        if url in seen_urls:
            continue
        seen_urls.add(url)

        start = max(0, match.start() - snippet_window)
        end = min(len(html), match.end() + snippet_window)
        snippet = strip_tags(html[start:end])[:280]

        posts.append({"url": url, "snippet": snippet})
    return posts


def load_state(state_file: str):
    if not os.path.exists(state_file):
        return {"seen_urls": []}
    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state_file: str, state) -> None:
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def send_email(to_addr: str, subject: str, body: str) -> None:
    gmail_user = os.environ.get("GMAIL_USER")
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD")
    if not gmail_user or not gmail_password:
        raise RuntimeError(
            "set GMAIL_USER and GMAIL_APP_PASSWORD environment variables to send email"
        )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = to_addr

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, [to_addr], msg.as_string())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page-url", default=DEFAULT_PAGE_URL, help="Facebook page URL to watch")
    parser.add_argument("--state-file", default=DEFAULT_STATE_FILE, help="Where to store seen posts")
    parser.add_argument("--to", required=True, help="Email address to notify")
    parser.add_argument("--dry-run", action="store_true", help="Print results instead of emailing")
    args = parser.parse_args()

    try:
        html = fetch_page(args.page_url)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if looks_like_login_wall(html):
        print(
            "WARNING: the page looks login-walled (Facebook is asking to log in). "
            "No posts could be read this run.",
            file=sys.stderr,
        )
        return 1

    posts = extract_posts(html, args.page_url)
    if not posts:
        print("No posts found on the page (markup may have changed, or nothing is public).")
        return 0

    state = load_state(args.state_file)
    seen_urls = set(state.get("seen_urls", []))
    new_posts = [p for p in posts if p["url"] not in seen_urls]

    # First run: just record what's there now, don't email a backlog dump.
    first_run = not state.get("seen_urls")

    seen_urls.update(p["url"] for p in posts)
    save_state(args.state_file, {"seen_urls": list(seen_urls)})

    if first_run:
        print(f"Initialized state with {len(posts)} existing post(s). Future runs will email new ones.")
        return 0

    if not new_posts:
        print("No new posts.")
        return 0

    body_lines = [f"New post(s) on {args.page_url}:\n"]
    for post in new_posts:
        body_lines.append(f"- {post['url']}\n  {post['snippet']}\n")
    body = "\n".join(body_lines)
    subject = f"New Facebook post: {args.page_url}"

    if args.dry_run:
        print(subject)
        print(body)
    else:
        send_email(args.to, subject, body)
        print(f"Emailed {len(new_posts)} new post(s) to {args.to}.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
