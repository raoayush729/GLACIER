import os
import time
import requests
from google import genai
from google.genai import types


# Configuration
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen3:4b-instruct-2507-q4_K_M"
GEMINI_MODEL = "gemini-2.5-flash"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in this terminal.")

gemini = genai.Client(api_key=GEMINI_API_KEY)

PROMPT = """
You are the language interpreter for GLACIER, a Python data-analysis assistant.

The active dataset is a CSV file containing sales records.

The user says:
"Show me the top five products by revenue."

Identify the appropriate action and return a concise JSON object containing:
- action
- reasoning
- arguments

Do not perform the analysis yourself.
Do not invent dataset values.
Return JSON only.
"""


def test_ollama():
    start = time.perf_counter()

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": PROMPT,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0,
                "num_predict": 200
            }
        },
        timeout=180
    )

    response.raise_for_status()
    data = response.json()

    total_time = time.perf_counter() - start

    prompt_tokens = data.get("prompt_eval_count", 0)
    output_tokens = data.get("eval_count", 0)

    prompt_time = data.get("prompt_eval_duration", 0) / 1e9
    generation_time = data.get("eval_duration", 0) / 1e9

    return {
        "model": "Local Qwen",
        "total_seconds": total_time,
        "prompt_tokens": prompt_tokens,
        "prompt_seconds": prompt_time,
        "output_tokens": output_tokens,
        "generation_seconds": generation_time,
        "tokens_per_second": (
            output_tokens / generation_time
            if generation_time > 0 else 0
        ),
        "response": data.get("response", "")
    }


def test_gemini():
    start = time.perf_counter()

    response = gemini.models.generate_content(
        model=GEMINI_MODEL,
        contents=PROMPT,
        config=types.GenerateContentConfig(
            temperature=0,
            max_output_tokens=200
        )
    )

    total_time = time.perf_counter() - start

    usage = response.usage_metadata

    input_tokens = (
        getattr(usage, "prompt_token_count", 0) or 0
    ) if usage else 0

    output_tokens = (
        getattr(usage, "candidates_token_count", 0) or 0
    ) if usage else 0

    return {
        "model": "Gemini 2.5 Flash",
        "total_seconds": total_time,
        "prompt_tokens": input_tokens,
        "prompt_seconds": None,
        "output_tokens": output_tokens,
        "generation_seconds": None,
        "tokens_per_second": None,
        "response": response.text or ""
    }


def display_result(result):
    print(f"\n{'=' * 55}")
    print(result["model"])
    print(f"{'=' * 55}")

    print(f"Total response time: {result['total_seconds']:.3f} seconds")
    print(f"Input tokens: {result['prompt_tokens']}")
    print(f"Output tokens: {result['output_tokens']}")

    if result["prompt_seconds"] is not None:
        print(
            "Prompt evaluation time: "
            f"{result['prompt_seconds']:.3f} seconds"
        )

    if result["generation_seconds"] is not None:
        print(
            "Generation time: "
            f"{result['generation_seconds']:.3f} seconds"
        )

    if result["tokens_per_second"] is not None:
        print(
            "Generation speed: "
            f"{result['tokens_per_second']:.2f} tokens/second"
        )

    print("\nModel response:")
    print(result["response"])


if __name__ == "__main__":
    print("Testing Qwen...")
    qwen_result = test_ollama()
    display_result(qwen_result)

    print("\nTesting Gemini...")
    gemini_result = test_gemini()
    display_result(gemini_result)