import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter
import config
import os
from utils.llm_client import LLMClient


def load_cards():
    cards = []
    with open(config.CARDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            cards.append(json.loads(line))
    return cards


def cluster_papers(cards, n_clusters=6):
    # 基于key_idea + method进行聚类
    texts = [f"{c.get('key_idea', '')} {c.get('method', '')}" for c in cards]
    vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
    X = vectorizer.fit_transform(texts)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)

    for i, card in enumerate(cards):
        card["cluster_id"] = int(labels[i])
    return cards


def generate_taxonomy(cards):
    """使用LLM为每个簇生成分类标签"""
    llm = LLMClient()
    taxonomy = {}

    for cluster_id in sorted(set(c["cluster_id"] for c in cards)):
        cluster_papers = [c for c in cards if c["cluster_id"] == cluster_id]
        sample_titles = [c["title"] for c in cluster_papers[:5]]

        prompt = f"""
Given these research paper titles from a cluster, suggest a concise category name (2-4 words) and a brief description (1 sentence) for this research sub-area.

Titles:
{chr(10).join('- ' + t for t in sample_titles)}

Output format:
Category: <name>
Description: <description>
"""
        response = llm.generate(prompt)
        lines = response.strip().split('\n')
        cat_name = lines[0].replace("Category:", "").strip()
        cat_desc = lines[1].replace("Description:", "").strip() if len(lines) > 1 else ""

        taxonomy[cluster_id] = {
            "name": cat_name,
            "description": cat_desc,
            "count": len(cluster_papers)
        }

    # 保存为markdown
    with open(config.TAXONOMY_FILE, "w", encoding="utf-8") as f:
        f.write("# Research Taxonomy\n\n")
        for cid, info in taxonomy.items():
            f.write(f"## {info['name']}\n")
            f.write(f"{info['description']} (n={info['count']})\n\n")

    print(f"✅ Taxonomy saved to {config.TAXONOMY_FILE}")
    return taxonomy


def generate_comparison_table(cards):
    """生成方法对比表"""
    df = pd.DataFrame([{
        "Title": c["title"][:50] + "...",
        "Method": c.get("method", "N/A"),
        "Dataset": c.get("dataset_or_scenario", "N/A"),
        "Metrics": ", ".join(c.get("metrics", [])) if isinstance(c.get("metrics"), list) else c.get("metrics", "N/A"),
        "Results": c.get("results_summary", "N/A"),
        "Limitations": c.get("limitations", "N/A"),
        "Category": c.get("best_fit_category", "N/A"),
        "Cluster": c.get("cluster_id", -1)
    } for c in cards])

    df.to_csv(config.COMPARISON_FILE, index=False, encoding="utf-8")
    print(f"✅ Comparison table saved to {config.COMPARISON_FILE}")
    return df


def run_analysis():
    if not os.path.exists(config.CARDS_FILE):
        print("❌ Cards not found. Run generate_cards.py first.")
        return

    cards = load_cards()
    print(f"Clustering {len(cards)} papers...")
    cards = cluster_papers(cards)

    # 更新卡片文件，加上cluster_id
    with open(config.CARDS_FILE, "w", encoding="utf-8") as f:
        for c in cards:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    taxonomy = generate_taxonomy(cards)
    df = generate_comparison_table(cards)
    return cards, taxonomy, df


if __name__ == "__main__":
    run_analysis()