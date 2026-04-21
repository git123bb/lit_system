import json
import os
from datetime import datetime
from collections import Counter
from utils.llm_client import LLMClient
import config


def load_data():
    cards = []
    with open(config.CARDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            cards.append(json.loads(line))

    with open(config.TAXONOMY_FILE, "r", encoding="utf-8") as f:
        taxonomy_md = f.read()

    import pandas as pd
    df = pd.read_csv(config.COMPARISON_FILE)
    return cards, taxonomy_md, df


def generate_digest():
    cards, taxonomy_md, df = load_data()
    llm = LLMClient()

    # 统计信息
    total_papers = len(cards)
    date_range = f"{min(c['published'][:10] for c in cards)} to {max(c['published'][:10] for c in cards)}"
    innovation_types = Counter(c.get("innovation_type", "Unknown") for c in cards)

    # 构建提示词
    summary_stats = f"""
- Total papers analyzed: {total_papers}
- Date range: {date_range}
- Innovation types distribution: {dict(innovation_types)}
"""

    # 选取代表性论文摘要
    sample_papers = []
    for c in cards[:10]:  # 取前10篇作为样例
        sample_papers.append(f"- {c['title']}: {c.get('key_idea', 'N/A')}")

    prompt = f"""
You are tasked with writing a weekly research survey digest (1-2 pages) based on an automated analysis of recent arXiv papers on "{config.QUERY}".

Here is the structured information:

## Statistics
{summary_stats}

## Research Taxonomy (from clustering)
{taxonomy_md}

## Sample Papers with Key Ideas
{chr(10).join(sample_papers)}

## Comparison Table Summary
The full comparison table includes {len(df)} papers with fields: Method, Dataset, Metrics, Results, Limitations.

Please generate a weekly survey digest in Markdown format with the following sections:
1. **Overview** - Brief summary of this week's paper collection
2. **Taxonomy & Key Themes** - Explain the main research directions
3. **Method Comparison Highlights** - Point out interesting contrasts in methods/datasets/results
4. **Emerging Trends** - What patterns do you observe?
5. **Research Gaps & Future Directions** - Provide ORIGINAL insights (not just summarizing papers). Suggest 2-3 concrete research directions that are underexplored based on the limitations observed.

The digest should be professional, concise (1-2 printed pages equivalent), and insightful.
"""

    print("Generating weekly digest with LLM...")
    digest = llm.generate(prompt,
                          system_prompt="You are a senior research scientist writing a weekly literature review for an AI lab.")

    # 添加头部信息
    header = f"""# Weekly Survey Digest: {config.QUERY.title()}
**Generated:** {datetime.now().strftime('%Y-%m-%d')}
**Papers Analyzed:** {total_papers}
**Period:** {date_range}

---
"""
    full_digest = header + digest

    with open(config.DIGEST_FILE, "w", encoding="utf-8") as f:
        f.write(full_digest)

    print(f"✅ Weekly digest saved to {config.DIGEST_FILE}")
    return full_digest


if __name__ == "__main__":
    generate_digest()