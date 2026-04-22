# Import Flask request/response utilities
from flask import Flask, request, jsonify

# Import your validation and sanitisation logic
from services.security import validate_input, sanitize

# Create Flask app FIRST
app = Flask(__name__)

@app.before_request
def security_layer():
    """
    Global middleware that runs BEFORE every request.

    Purpose:
    - Validate incoming user input
    - Detect prompt injection attempts
    - Strip unsafe HTML content
    - Block malicious requests early (return 400)

    This ensures that no unsafe input reaches routes or AI logic.
    """

    # Apply only to POST requests (AI endpoints use POST)
    if request.method != "POST":
        return  # Skip validation for GET/other requests

    # Safely parse JSON body (prevents crashes on invalid JSON)
    data = request.get_json(silent=True)

    # Reject if body is missing or invalid
    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # Support multiple possible input keys (team-safe design)
    # This ensures compatibility with future routes
    for key in ["input", "text", "query", "content"]:
        if key in data:
            value = data[key]

            # Validate input (type, length, injection detection)
            valid, error = validate_input(value)
            if not valid:
                return jsonify({"error": error}), 400

            # Sanitize input (remove HTML, trim spaces)
            # Store it in request context for safe usage in routes
            request.sanitized_input = sanitize(value)
            request.sanitized_key = key

            break  # Stop after first matching key