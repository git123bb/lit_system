import arxiv
import json
import os
from datetime import datetime, timedelta
from tqdm import tqdm
import config


def fetch_papers():
    os.makedirs(config.DATA_DIR, exist_ok=True)

    # 计算时间范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * config.YEAR_BACK)

    client = arxiv.Client()
    search = arxiv.Search(
        query=config.QUERY,
        max_results=config.MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    papers = []
    print(f"Fetching up to {config.MAX_RESULTS} papers on '{config.QUERY}'...")

    for result in tqdm(client.results(search), total=config.MAX_RESULTS):
        # 过滤时间
        if result.published.replace(tzinfo=None) < start_date:
            continue

        paper = {
            "arxiv_id": result.entry_id.split("/")[-1],
            "title": result.title,
            "authors": [str(a) for a in result.authors],
            "abstract": result.summary,
            "published": result.published.isoformat(),
            "categories": result.categories,
            "primary_category": result.primary_category,
            "pdf_url": result.pdf_url,
            "comment": result.comment or ""
        }
        papers.append(paper)

        if len(papers) >= 50:  # 保证至少50篇
            break

    # 按arxiv_id去重
    unique_papers = {p["arxiv_id"]: p for p in papers}
    papers = list(unique_papers.values())

    with open(config.RAW_FILE, "w", encoding="utf-8") as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(papers)} papers to {config.RAW_FILE}")
    return papers


if __name__ == "__main__":
    fetch_papers()