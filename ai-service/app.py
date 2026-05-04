from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from services.security import validate_input, sanitize

# Import all routes
from routes.query import query_bp
from routes.health import health_bp
from routes.report import report_bp
from routes.test_routes import test_bp

# Create app ONCE
app = Flask(__name__)

# Enable rate limit headers
app.config["RATELIMIT_HEADERS_ENABLED"] = True

# Rate limiter setup
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["30 per minute"]
)
limiter.init_app(app)

# Register ALL blueprints
app.register_blueprint(query_bp)
app.register_blueprint(health_bp)
app.register_blueprint(report_bp)
app.register_blueprint(test_bp)

# Handle rate limit errors
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        "error": "Too many requests. Please try again later."
    }), 429

# Global security middleware
@app.before_request
def security_layer():
    if request.method != "POST":
        return

    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    for key in ["input", "text", "query", "content"]:
        if key in data:
            value = data[key]

            valid, error = validate_input(value)
            if not valid:
                return jsonify({"error": error}), 400

            request.sanitized_input = sanitize(value)
            request.sanitized_key = key
            return

    return jsonify({"error": "Missing valid input field"}), 400

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "media-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    response.headers["Server"] = "SecureServer"
    return response

# Health route
@app.route("/")
def home():
    return "Server working"

# Run app ONCE
if __name__ == "__main__":
    print("Flask is starting...")
    app.run(debug=True, port=5000)