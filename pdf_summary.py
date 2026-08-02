# ============================================================
# pdf_summary.py - CLI PDF Summary Tool
# Xiangnan GAO
# ============================================================
"""
PDF Summary Tool.
Reads a PDF, sends its extracted text to an LLM via OpenRouter,
and prints a structured summary with exactly three sections:
Overview, Key Points, and Limitations.
Every key point must include a [Page X] citation.
"""
import argparse
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader


def parse_page_range(range_str, total_pages):
    """Parse a 'START-END' page range string and return (start, end).

    Raises SystemExit with a friendly message if the format or values are invalid.
    """
    if range_str is None:
        return 1, total_pages

    parts = range_str.split("-")
    if len(parts) != 2:
        raise SystemExit(
            f"Error: --pages must be in the format START-END (e.g., 1-5), "
            f"got '{range_str}'."
        )

    try:
        start = int(parts[0].strip())
        end = int(parts[1].strip())
    except ValueError:
        raise SystemExit(
            f"Error: --pages values must be numbers (e.g., 1-5), "
            f"got '{range_str}'."
        )

    if start < 1:
        raise SystemExit("Error: start page must be 1 or greater.")
    if end > total_pages:
        raise SystemExit(
            f"Error: end page ({end}) exceeds PDF total pages ({total_pages})."
        )
    if start > end:
        raise SystemExit(
            f"Error: start page ({start}) cannot be greater than end page ({end})."
        )

    return start, end


def extract_pages(pdf_path, page_range=None):
    """Extract text per page, numbered with [Page X] labels.

    If page_range is (start, end), only those pages are extracted.
    """
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        raise SystemExit(f"Error: could not open PDF: {e}")

    start, end = parse_page_range(page_range, len(reader.pages))

    total = len(reader.pages)
    numbered = []
    for i in range(start, end + 1):
        print(f"Extracting page {i}/{total}...", flush=True)
        page = reader.pages[i - 1]
        text = page.extract_text() or ""
        if text.strip():
            numbered.append(f"[Page {i}]\n{text.strip()}")
    return numbered


def build_prompt(numbered_text):
    """Build the system and user prompts for the summary request."""
    system_prompt = (
        "You are a precise document summarizer.\n"
        "Rules:\n"
        "1. Output exactly three sections: Overview, Key Points (3-5 bullets only), "
        "Limitations.\n"
        "2. After EVERY key point, add a citation in the format [Page X].\n"
        "3. Base everything ONLY on the provided PDF text.\n"
        "4. In Limitations, note anything the text does not cover or that "
        "could not be verified.\n"
        "5. Do NOT invent facts beyond what is in the text."
    )
    user_prompt = f"Here is the PDF text:\n\n{numbered_text}"
    return system_prompt, user_prompt


def summarize(numbered_text):
    """Call the LLM through OpenRouter and return the summary."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("Error: OPENROUTER_API_KEY is missing. Check your .env file.")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_prompt, user_prompt = build_prompt(numbered_text)

    try:
        response = client.chat.completions.create(
            model="google/gemma-4-26b-a4b-it:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise SystemExit(f"Error calling OpenRouter API: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Summarize a PDF into Overview, Key Points, and Limitations."
    )
    parser.add_argument("pdf_path", help="Path to the PDF file to summarize")
    parser.add_argument(
        "--pages",
        help="Page range to summarize (e.g., 1-5). Default: all pages.",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.pdf_path):
        raise SystemExit(f"Error: file not found: {args.pdf_path}")

    load_dotenv()

    # Extract text page by page. Never print the raw text to the console.
    numbered = extract_pages(args.pdf_path, page_range=args.pages)
    if not numbered:
        print(
            "No extractable text was found in the PDF. It may be a scanned "
            "document, so text extraction (and the LLM summary) was skipped."
        )
        return

    numbered_text = "\n\n".join(numbered)

    print("Summarizing...\n")
    summary = summarize(numbered_text)

    print(summary)


if __name__ == "__main__":
    main()
