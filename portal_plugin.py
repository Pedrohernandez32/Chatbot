from __future__ import annotations

import os
import json
import time
import re
from typing import Optional, Set

import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.robotparser as robotparser

load_dotenv()

CACHE_PATH = os.environ.get('PORTAL_CACHE_PATH', 'vector_store/portal_cache.json')
CACHE_TTL = int(os.environ.get('PORTAL_CACHE_TTL_HOURS', '24')) * 3600

DEFAULT_PORTAL = os.environ.get('UNIVERSITY_PORTAL_URL', 'https://www.udem.edu.co')
CRAWL_MAX_PAGES = int(os.environ.get('PORTAL_CRAWL_MAX_PAGES', '20'))
CRAWL_RATE_SECONDS = float(os.environ.get('PORTAL_CRAWL_RATE_SECONDS', '0.5'))


def _load_cache() -> dict:
    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(cache: dict) -> None:
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _can_fetch(url: str) -> bool:
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch('*', url)
    except Exception:
        return True


def _fetch_page(url: str, session: Optional[requests.Session] = None) -> Optional[str]:
    cache = _load_cache()
    now = time.time()
    if url in cache and now - cache[url].get('fetched_at', 0) < CACHE_TTL:
        return cache[url].get('text')

    if not _can_fetch(url):
        return None

    sess = session or requests.Session()
    headers = {'User-Agent': os.environ.get('PORTAL_USER_AGENT', 'udebot/1.0 (+https://www.udem.edu.co)')}
    try:
        resp = sess.get(url, timeout=8, headers=headers)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        for s in soup(['script', 'style', 'noscript']):
            s.decompose()
        text = soup.get_text(separator='\n')
        text = re.sub(r'\n\s+', '\n', text)

        cache[url] = {'fetched_at': now, 'text': text}
        _save_cache(cache)
        return text
    except Exception:
        return None


def _extract_links(base_url: str, html: str) -> Set[str]:
    soup = BeautifulSoup(html, 'html.parser')
    links: Set[str] = set()
    base_domain = urlparse(base_url).netloc
    for a in soup.find_all('a', href=True):
        href = a['href']
        full = urljoin(base_url, href)
        p = urlparse(full)
        if p.scheme not in ('http', 'https'):
            continue
        if p.netloc != base_domain:
            continue
        # remove fragment
        full = full.split('#')[0]
        links.add(full)
    return links


def _crawl_portal(start_url: str, max_pages: int = CRAWL_MAX_PAGES) -> dict:
    session = requests.Session()
    seen = set()
    to_visit = [start_url]
    pages = {}

    while to_visit and len(seen) < max_pages:
        url = to_visit.pop(0)
        if url in seen:
            continue
        html_text = _fetch_page(url, session=session)
        if not html_text:
            seen.add(url)
            continue
        pages[url] = html_text
        seen.add(url)
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            links = _extract_links(url, html_text)
            for l in links:
                if l not in seen and l not in to_visit and len(seen) + len(to_visit) < max_pages:
                    to_visit.append(l)
        except Exception:
            pass
        time.sleep(CRAWL_RATE_SECONDS)

    return pages


def _find_relevant_snippet_across_pages(pages: dict, prompt: str, max_sentences: int = 3) -> Optional[str]:
    tokens = set(re.findall(r"[\wáéíóúñ]+", prompt.lower()))
    if not tokens:
        return None

    best = None
    best_score = 0
    for url, text in pages.items():
        # split to sentences
        sentences = re.split(r'(?<=[.!?\n])\s+', text)
        # score by token overlap in contiguous window
        for i in range(len(sentences)):
            window = ' '.join(sentences[i:i+max_sentences]).lower()
            score = sum(1 for t in tokens if t in window)
            if score > best_score:
                best_score = score
                snippet = ' '.join(sentences[i:i+max_sentences]).strip()
                best = (url, snippet)

    if best and best_score > 0:
        url, snippet = best
        return f"Información encontrada en {url}:\n\n{snippet}\n\n(Extraído del portal oficial.)"
    return None


def portal_handler(prompt: str) -> Optional[str]:
    """Buscar información en el portal universitario configurado.

    Mejora: hace crawl respetuoso del dominio, cachea páginas y busca el fragmento
    más relevante entre las páginas visitadas.
    """
    urls_env = os.environ.get('UNIVERSITY_PORTAL_URLS')
    if urls_env:
        start_urls = [u.strip() for u in urls_env.split(',') if u.strip()]
    else:
        start_urls = [DEFAULT_PORTAL]

    all_pages = {}
    for start in start_urls:
        try:
            pages = _crawl_portal(start)
            all_pages.update(pages)
        except Exception:
            continue

    # Fallback: ensure at least the start page is present
    if not all_pages:
        txt = _fetch_page(start_urls[0])
        if txt:
            all_pages[start_urls[0]] = txt

    if not all_pages:
        return None

    snippet = _find_relevant_snippet_across_pages(all_pages, prompt)
    return snippet


def register(bot) -> None:
    bot.register_handler(portal_handler)
