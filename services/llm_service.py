import os

import anthropic


def generate_answer(question: str, passages: list[dict]) -> str:
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")

    context = "\n\n".join(
        f"[{p['source']} #{p['chunk_index']}]\n{p['text']}" for p in passages
    )
    prompt = (
        "Answer the question using ONLY the notes below. "
        "If the answer is not in the notes, say you don't know.\n\n"
        f"NOTES:\n{context}\n\nQUESTION: {question}"
    )
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as error:
        raise RuntimeError(f"LLM request failed: {error}")
    return response.content[0].text