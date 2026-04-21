from flask import Blueprint, request, jsonify
from services.groq_client import GroqClient
from services.chroma_client import query_docs
import time

query_bp = Blueprint("query", __name__)
client = GroqClient()

@query_bp.route("/query", methods=["POST"])
def query():
    start_time = time.time()
    
    question = request.json.get("question")

    # 🟢 Step 1: Get context
    results = query_docs(question)
    context = results.get("documents", [[]])[0]

    # 🟢 Step 2: Prompt (Day 6 tuned)
    prompt = f"""
    You are a professional Risk Analysis AI.

    STRICT RULES:
    - Use ONLY given context
    - Do NOT hallucinate
    - Answer clearly in 2-3 lines
    - Be precise and professional

    Context:
    {context}

    Question:
    {question}

    Return ONLY valid JSON:
    {{
      "answer": "...",
      "risk_type": "Financial | Operational | Security | Technical",
      "confidence": number (0-1)
    }}
    """

    # 🟢 Step 3: Call AI
    response = client.generate(prompt)

    # 🟢 Step 4: Fallback
    if not response:
        response = {
            "answer": "Unable to process",
            "risk_type": "Unknown",
            "confidence": 0.5
        }

    # 🟢 Step 5: Handle string/dict safely
    if isinstance(response, str):
        response = response.strip()

    end_time = time.time()

    # 🟢 Step 6: Return final output
    return jsonify({
        "result": response,
        "meta": {
            "response_time_ms": int((end_time - start_time) * 1000),
            "context_items": len(context),
            "model": "llama-3.3-70b-versatile"
        }
    })