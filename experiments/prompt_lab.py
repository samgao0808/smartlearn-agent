import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise SystemExit("OPENROUTER_API_KEY is missing. Add it to .env and try again.")

# Initialize the OpenAI-compatible client for OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def ask(prompt: str) -> str:
    """Send one prompt to the AI and return the answer text."""
    response = client.chat.completions.create(
        model="google/gemma-4-26b-a4b-it:free",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
    )
    return response.choices[0].message.content


# ============================================================
#  Three levels of prompts — topic: Python Lists
# ============================================================

# Level A: Vague Prompt
# TODO: write a vague question about Python lists
prompt_a = "Explain Valorant."  # <-- fill in the prompt here

# Level B: Structured Prompt (add a role + constraint)
# TODO: write a prompt with a role and a constraint
prompt_b = "You are a teacher major in games. Explain Valorant in 3 sentences."  # <-- fill in the prompt here

# Level C: Precise Prompt (role + constraint + output format)
# TODO: write a prompt with a role, a constraint, and an output format
prompt_c = "You are a teacher major in games. Explain Valorant in 3 sentences. Output format: 1. one sentence of introduction 2. one sentence of features 3. one sentence for famous player in China."  # <-- fill in the prompt here


# ============================================================
#  Run the experiment and print the results
# ============================================================
if __name__ == "__main__":
    prompts = {
        "Level A (Vague)": prompt_a,
        "Level B (Structured)": prompt_b,
        "Level C (Precise)": prompt_c,
    }

    for level, prompt in prompts.items():
        if not prompt:
            print(f"\n{'='*60}")
            print(f"  {level}: (empty -- fill in the TODO above!)")
            print(f"{'='*60}")
            continue

        print(f"\n{'='*60}")
        print(f"  {level}")
        print(f"  Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"{'='*60}")
        answer = ask(prompt)
        print(answer)