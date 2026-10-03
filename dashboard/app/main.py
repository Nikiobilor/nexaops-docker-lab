"""
NexaOps Internal Dashboard v1.0.0
Flask application showing service status, deployments, and team activity.
"""

import os
import json
import redis
import psycopg2
from datetime import datetime
from flask import Flask, jsonify, render_template

app = Flask(__name__, template_folder="../templates",
            static_folder="../static")

# ── Config ────────────────────────────────────────────────────────────────────
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "nexaops")
DB_USER = os.getenv("DB_USER", "nexaops")
DB_PASS = os.getenv("DB_PASSWORD", "nexaops")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


def get_redis():
    """Return a Redis connection or None if unavailable."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT,
                        decode_responses=True, socket_connect_timeout=2)
        r.ping()
        return r
    except Exception:
        return None


def get_db():
    """Return a PostgreSQL connection or None if unavailable."""
    try:
        return psycopg2.connect(
            host=DB_HOST, port=DB_PORT,
            dbname=DB_NAME, user=DB_USER, password=DB_PASS,
            connect_timeout=3
        )
    except Exception:
        return None


def get_services():
    """Return service status — from Redis cache or defaults."""
    r = get_redis()
    if r:
        cached = r.get("nexaops:services")
        if cached:
            return json.loads(cached)

    services = [
        {"name": "API Gateway", "status": "operational", "uptime": "99.98%"},
        {"name": "Authentication Service",
            "status": "operational", "uptime": "99.95%"},
        {"name": "Database Cluster", "status": "operational", "uptime": "99.99%"},
        {"name": "Payment Service", "status": "degraded", "uptime": "98.21%"},
        {"name": "Notification Service",
            "status": "operational", "uptime": "99.87%"},
        {"name": "File Storage", "status": "operational", "uptime": "99.94%"},
    ]

    if r:
        r.setex("nexaops:services", 30, json.dumps(services))

    return services


def get_deployments():
    """Return recent deployments from PostgreSQL or seed data."""
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT service, version, status, deployed_by, deployed_at
                FROM deployments
                ORDER BY deployed_at DESC
                LIMIT 5
            """)
            rows = cur.fetchall()
            conn.close()
            return [
                {"service": r[0], "version": r[1], "status": r[2],
                 "deployed_by": r[3], "deployed_at": str(r[4])}
                for r in rows
            ]
        except Exception:
            conn.close()

    return [
        {"service": "user-service", "version": "1.2.0", "status": "success",
         "deployed_by": "engineer-a", "deployed_at": "2024-01-15 09:32 UTC"},
        {"service": "notification-service", "version": "2.1.1", "status": "success",
         "deployed_by": "engineer-b", "deployed_at": "2024-01-15 08:15 UTC"},
        {"service": "payment-service", "version": "3.0.1", "status": "failed",
         "deployed_by": "engineer-c", "deployed_at": "2024-01-14 16:44 UTC"},
    ]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    services = get_services()
    deployments = get_deployments()
    operational = sum(1 for s in services if s["status"] == "operational")
    return render_template("index.html",
                           services=services,
                           deployments=deployments,
                           operational=operational,
                           total=len(services),
                           version=APP_VERSION,
                           environment=ENVIRONMENT,
                           timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                           )


@app.route("/health")
def health():
    redis_ok = get_redis() is not None
    db_ok = get_db() is not None
    return jsonify({
        "status": "healthy",
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "checks": {
            "redis": "connected" if redis_ok else "unavailable",
            "database": "connected" if db_ok else "unavailable"
        }
    }), 200


@app.route("/api/services")
def api_services():
    return jsonify(get_services())


@app.route("/api/deployments")
def api_deployments():
    return jsonify(get_deployments())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
