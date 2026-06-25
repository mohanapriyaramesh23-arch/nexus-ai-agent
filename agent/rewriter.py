import os
from google import genai
from google.genai import types

def rewrite_query(user_query: str, history_string: str) -> str:
    """
    Analyzes a user's question alongside conversation history. If the query is ambiguous,
    it rewrites it into a self-contained question using the modern Google GenAI library.
    """
    system_instruction = (
        "You are an expert query reformulation assistant. Your job is to read a conversation history "
        "and a raw follow-up user query, and output a completely self-contained, standalone search query.\n\n"
        "STRICT CRITERIA:\n"
        "1. Resolve all pronoun references (e.g., change 'it', 'this', 'that', 'its operational limits' to the explicit noun named in history).\n"
        "2. If the user query is already self-contained, or if the user switches to an completely new topic unrelated to the history, do NOT modify it. Output it verbatim.\n"
        "3. If the history is empty or contains no relevant context, output the query completely unchanged.\n"
        "4. Return ONLY the rewritten text string. Do not append any commentary, explanations, prefixes, or markdown formatting."
    )

    prompt = f"""
History Context:
{history_string}

Incoming User Query: {user_query}

Rewritten Query:"""

    try:
        # Using the standard modern client initialization
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0,
            ),
        )
        return response.text.strip()
    except Exception as e:
        print(f"[WARNING] Query rewriter encountered an error: {e}. Falling back to raw query.")
        return user_query