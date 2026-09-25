import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ_API_KEY is missing")
    raise SystemExit(1)

try:
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: GROQ_INSURA_TEST_WORKING"
            }
        ],
    )

    print("✅ GROQ MODEL WORKS")
    print("MODEL: openai/gpt-oss-120b")
    print("RESPONSE:", response.choices[0].message.content)

except Exception as e:
    print("❌ GROQ MODEL TEST FAILED")
    print("ERROR TYPE:", type(e).__name__)
    print("ERROR:", str(e))