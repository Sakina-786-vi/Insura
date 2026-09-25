import os
from dotenv import load_dotenv
import litellm

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

print("=== GROQ + LITELLM TEST ===")

try:
    response = litellm.completion(
        model="groq/qwen/qwen3.8-27b",
        api_key=api_key,
        api_base="https://api.groq.com/openai/v1",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: INSURA_GROQ_LITELLM_WORKS"
            }
        ],
    )

    print("✅ SUCCESS")
    print(response.choices[0].message.content)

except Exception as e:
    print("❌ FAILED")
    print("ERROR TYPE:", type(e).__name__)
    print("ERROR:", str(e))