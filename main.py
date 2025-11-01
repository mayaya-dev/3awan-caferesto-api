import os
from flask import Flask
from flask_cors import CORS
import logging

# Import our blueprint and database
from app.routes.web import web
from app.config.database import db


app = Flask(__name__)

# Configure Flask settings
app.config.update(
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key-123')
)
# Ensure exceptions propagate so our error handlers/logging can capture them
app.config['PROPAGATE_EXCEPTIONS'] = True

# Configure application logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("3awan")
logger.info("Starting 3awan CafeResto API")

# Initialize extensions
db.init_app(app)

# Import all model modules to ensure SQLAlchemy relationships/backrefs are registered
from app.models import category, menu, order, order_item  # noqa: F401

# Configure CORS (dapat dikonfigurasi via env CORS_ORIGINS)
origins_env = os.environ.get("CORS_ORIGINS", app.config.get('CORS_ORIGINS', '*'))
if origins_env.strip() == "*":
    allowed_origins = "*"
else:
    allowed_origins = [o.strip() for o in origins_env.split(",") if o.strip()]

CORS(
    app,
    resources={
        r"/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "Accept",
                "Origin",
                "Cache-Control",
                "Pragma",
            ],
            "expose_headers": [
                "Content-Type",
                "Authorization",
            ],
        }
    },
    supports_credentials=False,
    send_wildcard=(allowed_origins == "*"),
    max_age=86400,
)

# Buat tabel otomatis jika belum ada (di context aplikasi)
with app.app_context():
    try:
        db.create_all()
    except Exception:
        # Jika database tidak terkonfigurasi/terjangkau, tetap lanjutkan
        logger.exception("Failed to run db.create_all()")
        pass

# Daftarkan blueprint
app.register_blueprint(web)

# Debug route to list all registered URL rules
@app.route('/debug_routes', methods=['GET'])
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "rule": str(rule),
            "endpoint": rule.endpoint,
            "methods": sorted(list(rule.methods))
        })
    return {"routes": routes}, 200

# Global error handlers to surface exceptions clearly
@app.errorhandler(Exception)
def handle_exception(e):
    logging.getLogger("3awan").exception("Unhandled exception")
    try:
        # Return JSON error payload
        return {"error": str(e)}, 500
    except Exception:
        # Fallback to plain text if jsonify fails
        return "Internal Server Error", 500

# Basic request logging to trace endpoints
@app.before_request
def log_request_start():
    logging.getLogger("3awan").info(f"Request start: {os.environ.get('REQUEST_ID','')} {__name__}")

@app.after_request
def log_request_end(response):
    logging.getLogger("3awan").info(f"Request end: status={response.status_code} content_type={response.content_type}")
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Jalankan pada 0.0.0.0 agar dapat diakses dari luar (mis. platform hosting)
    app.run(host="0.0.0.0", port=port)