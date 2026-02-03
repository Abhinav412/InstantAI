import re
import pandas as pd

from web_ingestion.planning.crawl_intent import resolve_crawl_intent
from web_ingestion.planning.coverage_planner import CoveragePlanner

from web_ingestion.discovery.search_client import search_urls as search
from web_ingestion.discovery.url_queue import URLQueue

from web_ingestion.extraction.fetcher import fetch_html as fetch
from web_ingestion.extraction.content_parser import extract_text

from web_ingestion.preprocessing.normalizer import normalize_rows
from web_ingestion.preprocessing.deduplicator import deduplicate

from pipeline.dataset_pipeline import process_user_dataset


# -------------------------------------------------
# Simple query builder
# -------------------------------------------------
def build_queries(intent):
    base = intent.entity

    queries = [
        f"top {base}",
        f"{base} list",
        f"best {base}",
        f"leading {base}",
    ]

    if intent.geo:
        queries = [q + f" {intent.geo}" for q in queries]

    return list(set(queries))


# -------------------------------------------------
# VERY permissive name extractor (ranking-friendly)
# -------------------------------------------------
def extract_names(text: str) -> list[str]:
    names = set()

    for line in text.splitlines():
        line = line.strip()

        # numbered or bulleted list
        if (
            re.match(r"^\d+[\.\)]\s+[A-Z]", line)
            or line.startswith(("-", "•", "*"))
        ):
            # remove bullets / numbers
            name = re.sub(r"^[\d\.\)\-\•\*]+\s*", "", line)

            # remove trailing description
            name = re.split(r"[-–—:|]", name, maxsplit=1)[0].strip()

            # basic sanity checks
            if 3 <= len(name) <= 60 and any(c.isupper() for c in name):
                names.add(name)

    return list(names)


# -------------------------------------------------
# MAIN INGESTION FUNCTION
# -------------------------------------------------
def run_web_ingestion(user_query: str):
    intent = resolve_crawl_intent(user_query)
    queries = build_queries(intent)

    url_queue = URLQueue()
    coverage = CoveragePlanner(intent.entity)

    # -------------------------------
    # 1. DISCOVERY (Google Search)
    # -------------------------------
    for q in queries:
        urls = search(q)
        if urls:
            url_queue.add_many(urls)

    rows = []

    # -------------------------------
    # 2. FETCH + EXTRACT
    # -------------------------------
    while url_queue.has_next() and not coverage.satisfied():
        url = url_queue.next()

        html = fetch(url)
        if not html:
            continue

        text = extract_text(html)
        names = extract_names(text)

        for name in names:
            row = {
                "name": name,
                "_source": url,
            }
            rows.append(row)
            coverage.update([row])

    # -------------------------------
    # 3. POST-PROCESSING
    # -------------------------------
    rows = deduplicate(rows)
    rows = normalize_rows(rows)

    if not rows:
        raise RuntimeError(
            "Web ingestion failed: no candidates found from search results"
        )

    # -------------------------------
    # 4. PIPELINE INJECTION (DKL)
    # -------------------------------
    df = pd.DataFrame(rows)

    return process_user_dataset(
        file_path=None,
        injected_df=df,
        dataset_origin="web",
    )
