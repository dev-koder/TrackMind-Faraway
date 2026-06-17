import json
import os

import anthropic


async def call_claude(system_prompt: str, user_content: str) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_key_here":
        raise ValueError("Anthropic API key not configured")

    client = anthropic.AsyncAnthropic(api_key=api_key)

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_content}
        ],
    )

    response_text = message.content[0].text

    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]

    return json.loads(response_text.strip())
