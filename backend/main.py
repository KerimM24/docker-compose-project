from flask import Flask, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import json
import time
from datetime import datetime

app = Flask(__name__)

APP_NAME = os.environ.get("APP_NAME", "unknown-app")
APP_VERSION = os.environ.get("APP_VERSION", "0.0")
APP_ENVIRONMENT = os.environ.get("APP_ENVIRONMENT", "unknown")

DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_QUEUE_KEY = os.environ.get("REDIS_QUEUE_KEY", "jobs")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,  
    )


@app.route("/")
def index():
    return jsonify(
        app_name=APP_NAME,
        version=APP_VERSION,
        environment=APP_ENVIRONMENT,
        message="Hello iz Docker + Compose + Postgres + Redis backend-a!"
    )


@app.route("/health")
def health():
    return jsonify(status="ok")


@app.route("/db-test")
def db_test():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name TEXT
            );
            """
        )

        cur.execute(
            "INSERT INTO test_table (name) VALUES (%s);",
            ("Kerim",)
        )

        conn.commit()

        cur.execute("SELECT COUNT(*) AS count FROM test_table;")
        result = cur.fetchone()

        cur.close()
        conn.close()

        return jsonify(
            message="DB radi!",
            total_rows=result["count"]
        )

    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/enqueue")
def enqueue():
    try:
        r = get_redis_client()

        job = {
            "id": f"job-{int(time.time() * 1000)}",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "payload": "neki test payload"
        }

        r.lpush(REDIS_QUEUE_KEY, json.dumps(job))

        queue_length = r.llen(REDIS_QUEUE_KEY)

        return jsonify(
            message="Job dodan u queue",
            job=job,
            queue_length=queue_length
        )

    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route("/queue-stats")
def queue_stats():

    try:
        r = get_redis_client()
        queue_length = r.llen(REDIS_QUEUE_KEY)

        return jsonify(
            queue_key=REDIS_QUEUE_KEY,
            queue_length=queue_length
        )

    except Exception as e:
        return jsonify(error=str(e)), 500


if __name__ == "__main__":
    port = int(os.environ.get("BACKEND_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
