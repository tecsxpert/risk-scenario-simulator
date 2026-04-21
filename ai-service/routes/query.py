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

    # Step 1: Retrieve context
    results = query_docs(question)
    context = results["documents"][0]

    # Step 2: Better structured prompt
    prompt = f"""
    You are an expert risk analysis AI.

    Use ONLY the context below to answer.

    Context:
    {context}

    Question:
    {question}

    Give output in JSON:
    {{
        "answer": "...",
        "risk_type": "...",
        "confidence": 0-1
    }}
    """

    # Step 3: Generate answer
    response = client.generate(prompt)

    end_time = time.time()

    return jsonify({
        "result": response,
        "meta": {
            "response_time_ms": int((end_time - start_time) * 1000),
            "context_items": len(context),
            "model": "llama-3.3-70b-versatile"
        }
    })