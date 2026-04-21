import json
import os
from tqdm import tqdm
from utils.llm_client import LLMClient
import config

CARD_SCHEMA = {
    "title": "string",
    "problem": "string (research problem addressed)",
    "key_idea": "string (core innovation in one sentence)",
    "method": "string (technical approach)",
    "dataset_or_scenario": "string",
    "metrics": "list of strings",
    "results_summary": "string (quantitative findings)",
    "innovation_type": "string (e.g., architectural, algorithmic, theoretical)",
    "limitations": "string",
    "best_fit_category": "string (suggested research sub-area)",
    "confidence_level": "string (high/medium/low)"
}

PROMPT_TEMPLATE = """
Given the following paper abstract, extract structured information in JSON format.
Only use information from the abstract, do not invent details. If a field is not mentioned, write "Not specified".

Paper Title: {title}
Abstract: {abstract}

Output strictly as JSON with these fields:
{fields}

JSON:
"""


def generate_card(paper, llm):
    prompt = PROMPT_TEMPLATE.format(
        title=paper["title"],
        abstract=paper["abstract"],
        fields="\n".join([f"- {k}: {v}" for k, v in CARD_SCHEMA.items()])
    )

    try:
        response = llm.generate(prompt)
        # 提取JSON部分
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        card_data = json.loads(response[json_start:json_end])

        # 添加原始信息
        card_data["arxiv_id"] = paper["arxiv_id"]
        card_data["published"] = paper["published"]
        return card_data
    except Exception as e:
        print(f"Error processing {paper['arxiv_id']}: {e}")
        return None


def generate_all_cards():
    if not os.path.exists(config.RAW_FILE):
        print("❌ Raw papers not found. Run fetch_arxiv.py first.")
        return

    with open(config.RAW_FILE, "r", encoding="utf-8") as f:
        papers = json.load(f)

    llm = LLMClient()
    cards = []

    print(f"Generating structured cards for {len(papers)} papers...")
    for paper in tqdm(papers):
        card = generate_card(paper, llm)
        if card:
            cards.append(card)

    # 保存为JSONL
    with open(config.CARDS_FILE, "w", encoding="utf-8") as f:
        for card in cards:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")

    print(f"✅ Generated {len(cards)} cards -> {config.CARDS_FILE}")
    return cards


if __name__ == "__main__":
    generate_all_cards()