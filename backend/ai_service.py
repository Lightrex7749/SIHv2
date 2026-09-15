"""
DrishtiSetu — OpenRouter AI Consultation & Decision Synthesis Engine
Powered by OpenAI SDK via OpenRouter.
Model: nvidia/nemotron-3-ultra-550b-a55b:free (with resilient fallbacks)
"""

import os
from typing import Dict, Any, Optional, Iterator
from openai import OpenAI

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
PRIMARY_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")

FALLBACK_MODELS = [
    PRIMARY_MODEL,
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.0-flash-exp:free"
]

client = OpenAI(
    base_url=OPENROUTER_BASE_URL,
    api_key=OPENROUTER_API_KEY,
)


SYSTEM_PROMPT = """You are DrishtiSetu AI, an expert Senior Disaster Management and Relocation Advisor for State Disaster Management Authorities (SDMAs) in India.
Your mission is to provide rigorous, actionable, legally sound, and scientifically grounded relocation decision-support.

RULES:
1. Always respect physical carrying capacity and deterministic safety checks. Never claim a site has sufficient capacity if a capacity deficit was computed.
2. Ground guidance in Indian statutory frameworks: Disaster Management Act 2005, NDMA Guidelines (Landslides 2009, Floods 2008), and the National Rehabilitation and Resettlement Policy (2007).
3. Be professional, structured, concise, and direct. Use bullet points and clear headings.
"""


def generate_ai_consultation(
    query: str,
    habitation_context: Optional[Dict[str, Any]] = None,
    decision_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates an expert AI consultation response using the configured OpenRouter model.
    """
    context_str = ""
    if habitation_context:
        context_str += (
            f"\nHABITATION DATA:\n"
            f"- Name: {habitation_context.get('name')}\n"
            f"- District/State: {habitation_context.get('district')}, {habitation_context.get('state')}\n"
            f"- Population: {habitation_context.get('population')} persons\n"
            f"- Risk Level: {habitation_context.get('risk_level')} (Score: {habitation_context.get('risk_score')})\n"
            f"- Hazard Type: {habitation_context.get('hazard_type')}\n"
            f"- Elevation: {habitation_context.get('elevation')}m, Slope: {habitation_context.get('slope')}°\n"
        )
    if decision_context:
        context_str += (
            f"\nDECISION ENGINE RECOMMENDATION:\n"
            f"- Recommended Site: {decision_context.get('relocation', {}).get('recommended_site')}\n"
            f"- Capacity Sufficient: {decision_context.get('relocation', {}).get('capacity_sufficient')}\n"
            f"- Land-Use Conflict: {decision_context.get('relocation', {}).get('land_use_conflict')}\n"
            f"- Recommendation: {decision_context.get('recommendation')}\n"
        )

    user_message = f"{context_str}\nUSER INQUIRY / DIRECTIVE:\n{query}" if context_str else query

    last_error = None
    for model_name in FALLBACK_MODELS:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=650,
            )
            if completion.choices and completion.choices[0].message and completion.choices[0].message.content:
                return {
                    "answer": completion.choices[0].message.content.strip(),
                    "model": model_name,
                    "provider": "OpenRouter",
                    "status": "success"
                }
        except Exception as e:
            last_error = e
            continue

    # Graceful offline deterministic fallback if network / free-tier is temporarily unavailable
    fallback_context = habitation_context or {}
    return {
        "answer": (
            f"Based on DrishtiSetu statutory guidelines for {fallback_context.get('name', 'this situation')}: "
            f"Relocation priority is {fallback_context.get('relocation_priority', 'HIGH')}. "
            f"Per Section 12 of National R&R Policy 2007, safe recipient sites must provide potable water, road access, and educational transit before displacement."
        ),
        "model": "rule_based_fallback",
        "provider": "offline",
        "status": "fallback",
        "error": str(last_error) if last_error else None
    }


def stream_ai_consultation(
    query: str,
    habitation_context: Optional[Dict[str, Any]] = None
) -> Iterator[str]:
    """
    Streams AI consultation tokens using OpenRouter.
    """
    context_str = ""
    if habitation_context:
        context_str = (
            f"Habitation: {habitation_context.get('name')} (Pop: {habitation_context.get('population')}, "
            f"Risk: {habitation_context.get('risk_level')})\n"
        )

    user_message = f"{context_str}Query: {query}" if context_str else query

    try:
        stream = client.chat.completions.create(
            model=PRIMARY_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            stream=True,
            temperature=0.3,
            max_tokens=500
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        # Stream fallback if model is temporarily overloaded
        yield f"\n[AI stream notification: {str(e)}]\n"
        fallback = generate_ai_consultation(query, habitation_context)
        yield fallback["answer"]
