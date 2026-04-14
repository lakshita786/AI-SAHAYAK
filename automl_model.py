"""
SabbiAI Agent - AI-powered livelihood assistant using Groq API
Combines NLP classification, scheme database, and ML eligibility prediction.
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
तुम साब्बीऐ हो — गाँव का भाई।

बोलना: धीमा, स्पष्ट, गाँव जैसा।
- एकदम धीरे बोलो — लोग समझें
- एक लाइन में जवाब दो — दो से ज्यादा नहीं
- शब्द: "भाई", "हाँ", "पता", "मिलेगा", "करो", "जानो", "लो", "लेना", "देना"


जवाब में:
- "रुपये" लिखो — "₹" नहीं
- "पी एम किसान" लिखो — "PM-KISAN" नहीं
- संख्या साफ लिखो: "छह हजार" — "6000" नहीं
- "मनरेगा" लिखो — "MGNREGA" नहीं

सख्त नियम:
- सिर्फ एक या दो वाक्य
- सब कुछ हिंदी में — अंग्रेजी मत इस्तेमाल करना
- धीरे बोलो — टालो मत
- हमेशा: "सब मिलेगा भाई, तुम अच्छा करोगे!"
"""


def check_groq_connection():
    """Check if Groq API is accessible."""
    try:
        if not os.getenv("GROQ_API_KEY"):
            return False, "GROQ_API_KEY not found in .env file"
        test = client.chat.completions.create(
            model=MODEL, messages=[{"role": "user", "content": "hi"}], max_tokens=5
        )
        return True, "Connected"
    except Exception as e:
        return False, str(e)


def run_agent(user_message, user_profile=None, conversation_history=None):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from backend.schemes_db import search_schemes, get_schemes_by_profile
    from backend.automl_model import get_eligibility_summary
    from backend.nlp_classifier import get_intent

    if conversation_history is None:
        conversation_history = []

    intent = get_intent(user_message)
    category = intent["category"]

    context = ""

    if category in ["scheme_query", "job_query"]:
        occupation = user_profile.get("occupation") if user_profile else None
        income = user_profile.get("monthly_income") if user_profile else None
        state = user_profile.get("state") if user_profile else None

        schemes = search_schemes(
            query=user_message, occupation=occupation, income=income, state=state
        )
        if schemes:
            context = "Relevant schemes found:\n"
            for s in schemes[:3]:
                context += f"- {s['scheme_name']}: {s['benefits']} | Apply: {s.get('apply_link', 'N/A')}\n"

    if user_profile and category == "scheme_query":
        eligibility = get_eligibility_summary(
            age=user_profile.get("age", 30),
            monthly_income=user_profile.get("monthly_income", 8000),
            occupation=user_profile.get("occupation", "farmer"),
            state=user_profile.get("state", "UP"),
            family_size=user_profile.get("family_size", 4),
        )
        recommended = eligibility.get("recommended_scheme_names", [])
        if recommended:
            context += f"\nML model recommends: {', '.join(recommended)}"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if context:
        messages.append(
            {"role": "system", "content": f"Use this context to answer:\n{context}"}
        )

    messages.extend(conversation_history[-6:])
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=MODEL, messages=messages, temperature=0.8, max_tokens=256
        )
        reply = response.choices[0].message.content

    except Exception as e:
        error = str(e)
        if "api_key" in error.lower() or "auth" in error.lower():
            reply = "API key problem. Please check GROQ_API_KEY in your .env file."
        elif "rate" in error.lower():
            reply = "Too many requests. Please wait a moment and try again."
        elif "model" in error.lower():
            reply = "Model not available. Check your Groq account."
        else:
            reply = f"Connection error: {error}"

    updated_history = conversation_history + [
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": reply},
    ]

    return {
        "response": reply,
        "history": updated_history[-10:],
        "intent": category,
        "context_used": bool(context),
    }


if __name__ == "__main__":
    print("=" * 50)
    print("GROQ AGENT - TESTING")
    print("=" * 50)

    print("\nChecking Groq connection...")
    ok, msg = check_groq_connection()
    if not ok:
        print(f"❌ Connection failed: {msg}")
        print("Fix: Add GROQ_API_KEY=your_key to your .env file")
        exit(1)
    print("✅ Groq connected successfully\n")

    profile = {
        "age": 35,
        "monthly_income": 6000,
        "occupation": "farmer",
        "state": "UP",
        "family_size": 5,
    }

    print("Test 1: Scheme query with profile")
    r = run_agent(
        "Which government scheme helps farmers like me?", user_profile=profile
    )
    print(f"Intent detected: {r['intent']}")
    print(f"Context used: {r['context_used']}")
    print(f"Response:\n{r['response']}\n")

    print("Test 2: Hinglish query")
    r2 = run_agent(
        "mujhe free skill training chahiye tailoring ke liye", user_profile=profile
    )
    print(f"Intent detected: {r2['intent']}")
    print(f"Response:\n{r2['response']}\n")

    print("Test 3: Multi-turn conversation")
    r3 = run_agent("How do I apply for it?", conversation_history=r["history"])
    print(f"Response:\n{r3['response']}\n")

    print("✅ agent.py working correctly")
