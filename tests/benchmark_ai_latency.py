import time
import statistics

from app.ticker import fetch_company_context
from app.chat import answer_company_question
from app.ollama_client import answer_with_ollama

company = fetch_company_context("NVDA")

QUESTIONS = [
    "Summarize NVIDIA's financial health in 5 bullet points.",
    "Explain NVIDIA's valuation in simple English.",
    "What are NVIDIA's biggest financial strengths?"
]


def benchmark_gemini(advanced=False):
    times = []

    print("\n==============================")
    print("Gemini Flash" if advanced else "Gemini Flash Lite")
    print("==============================")

    for q in QUESTIONS:
        start = time.perf_counter()

        answer_company_question(
            company_context=company,
            user_question=q,
            advanced=advanced,
        )

        elapsed = time.perf_counter() - start
        times.append(elapsed)

        print(f"{elapsed:.2f}s | {q}")

    return times


def benchmark_ollama():
    times = []

    print("\n==============================")
    print("Ollama")
    print("==============================")

    for q in QUESTIONS:
        start = time.perf_counter()

        answer_with_ollama(
            user_question=q,
            company_context=company,
            model_name="llama3",
        )

        elapsed = time.perf_counter() - start
        times.append(elapsed)

        print(f"{elapsed:.2f}s | {q}")

    return times


def summarize(name, values):
    print(f"\n{name}")
    print("-" * 35)
    print(f"Average : {statistics.mean(values):.2f}s")
    print(f"Median  : {statistics.median(values):.2f}s")
    print(f"Fastest : {min(values):.2f}s")
    print(f"Slowest : {max(values):.2f}s")


flash_lite = benchmark_gemini(False)
flash = benchmark_gemini(True)
ollama = benchmark_ollama()

print("\n==============================")
print("BENCHMARK SUMMARY")
print("==============================")

summarize("Gemini Flash Lite", flash_lite)
summarize("Gemini Flash", flash)
summarize("Ollama", ollama)