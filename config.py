import os
from dotenv import load_dotenv

load_dotenv()

# arXiv查询配置
QUERY = "quantum computing"  # 研究方向关键词
MAX_RESULTS = 60                # 抓取数量（略多于50以防去重）
YEAR_BACK = 2                   # 回溯年数

# LLM配置 (支持OpenAI / Claude / 本地)
LLM_PROVIDER = "openai"         # "openai", "claude", "local"
OPENAI_API_KEY = "sk-3e5b7aa95b8d4d15ace3d22ce00dc170"
#ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 路径配置
DATA_DIR = "data"
RAW_FILE = os.path.join(DATA_DIR, "papers_raw.json")
CARDS_FILE = os.path.join(DATA_DIR, "paper_cards.jsonl")
TAXONOMY_FILE = os.path.join(DATA_DIR, "taxonomy.md")
COMPARISON_FILE = os.path.join(DATA_DIR, "comparison_table.csv")
DIGEST_FILE = os.path.join(DATA_DIR, "weekly_digest.md")