import sys
from fetch_arxiv import fetch_papers
from generate_cards import generate_all_cards
from cluster_analysis import run_analysis
from weekly_survey_generator import generate_digest


def run_pipeline():
    print("🚀 Starting Automated Literature Review Pipeline\n")

    print("=" * 50)
    print("STEP 1: Fetching papers from arXiv")
    print("=" * 50)
    fetch_papers()

    print("\n" + "=" * 50)
    print("STEP 2: Generating structured cards")
    print("=" * 50)
    generate_all_cards()

    print("\n" + "=" * 50)
    print("STEP 3: Clustering and taxonomy")
    print("=" * 50)
    run_analysis()

    print("\n" + "=" * 50)
    print("STEP 4: Generating weekly digest")
    print("=" * 50)
    digest = generate_digest()

    print("\n✅ Pipeline completed successfully!")
    print(f"📄 Final output: data/weekly_digest.md")


if __name__ == "__main__":
    run_pipeline()