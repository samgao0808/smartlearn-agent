# ============================================================
# cli_qa.py - CLI Q&A Tool with Paragraph Citations
# ============================================================
"""
CLI Q&A Tool.
Paste multi-paragraph text, ask a question, and get an LLM answer
with [Paragraph X] citations via OpenRouter.
"""
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def read_text():
    """Read multi-line text from the user until END is typed."""
    print("请粘贴文本（输入 END 结束）：")
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    return "\n".join(lines)


def split_paragraphs(text):
    """Split text into paragraphs by blank lines, filter out empties."""
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def number_paragraphs(paragraphs):
    """Number paragraphs and return a single formatted string."""
    numbered = []
    for i, para in enumerate(paragraphs, 1):
        numbered.append(f"[Paragraph {i}]\n{para}")
    return "\n\n".join(numbered)


def ask_question(numbered_text, question):
    """Build the prompt, call the LLM API, return the answer."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("Error: OPENROUTER_API_KEY is missing. Check your .env file.")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_prompt = (
        "You are a precise research assistant.\n"
        "Rules:\n"
        "1. Answer ONLY using information from the provided text.\n"
        "2. After EVERY claim, add a citation in the format [Paragraph X].\n"
        "3. If a sentence uses information from multiple paragraphs, cite all of them.\n"
        "4. If the text does not contain the answer, reply exactly:\n"
        "   'The text does not provide this information.'\n"
        "5. Do NOT add any information beyond what is in the text."
    )

    user_prompt = f"Here is the text:\n\n{numbered_text}\n\nQuestion: {question}"

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
    # ---- Parse command-line arguments ----
    parser = argparse.ArgumentParser(description="CLI Q&A Tool")
    parser.add_argument(
        "--file",
        help="Path to a text file to use as input (instead of pasting)",
    )
    args = parser.parse_args()

    # ---- Read the text ----
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
        print(f"已从文件 {args.file} 读取文本。")
    else:
        text = read_text()

    paragraphs = split_paragraphs(text)
    print(f"\n检测到 {len(paragraphs)} 个段落。")

    numbered_text = number_paragraphs(paragraphs)

    # ---- Q&A loop ----
    print("你可以连续提问，输入 quit 退出。\n")

    while True:
        question = input("请输入你的问题（quit 退出）：")

        if question.strip().lower() == "quit":
            print("再见！")
            break

        print("\n正在思考...\n")
        answer = ask_question(numbered_text, question)

        print("回答：")
        print(answer)
        print()  # Blank line to visually separate each round


if __name__ == "__main__":
    main()
