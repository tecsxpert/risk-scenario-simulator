from flask import Blueprint, request, jsonify
from services.groq_client import GroqClient
from services.redis_client import get_cache, set_cache, redis_available
from services.logger import logger
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
query_bp = Blueprint("query", __name__)

@query_bp.route("/query", methods=["POST"])
def query():
    try:
        question = request.json.get("question")

        if not question:
            return jsonify({"error": "Question is required"}), 400

        #  Normalize question (VERY IMPORTANT)
        question = question.strip().lower()

        logger.info(f"Received question: {question}")
        print("Redis available:", redis_available)

        #  Cache key
        cache_key = f"query:{question}"

        #  CHECK CACHE
        cached = get_cache(cache_key)

        if cached:
            logger.info("Cache HIT")
            print("Cache HIT")
            return jsonify({
                "result": json.loads(cached),
                "cached": True,
                "meta": {"is_fallback": False}
            })

        logger.info("Cache MISS")
        print("Cache MISS")

        # CREATE CLIENT
        client = GroqClient()

        # PROMPT
        prompt_path = os.path.join("prompts", "risk_prompt.txt")
        with open(prompt_path, "r") as f:
            template = f.read()

        prompt = template.format(question=question)

        try:
            logger.info("Calling AI model")

            ai_response = client.generate(prompt)

            response = ai_response.get("result")
            meta = ai_response.get("meta", {})
            is_fallback = meta.get("is_fallback", False)

        except Exception as e:
            logger.warning("AI failed, using fallback")

            response = {
                "answer": "Potential risk detected. Further analysis recommended.",
                "risk_type": "General",
                "confidence": 0.5
            }

            meta = {"error": str(e)}
            is_fallback = True

        #  Ensure JSON format
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except:
                response = {
                    "answer": response,
                    "risk_type": "Unknown",
                    "confidence": 0.6
                }
        #  STORE IN REDIS (ONLY IF NOT FALLBACK)
        if not is_fallback:
            set_cache(cache_key, json.dumps(response))
            print("Stored in cache")

        logger.info("Response generated")

        return jsonify({
            "result": response,
            "sources": [],
            "meta": {
                **meta,
                "is_fallback": is_fallback
            },
            "cached": False
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
