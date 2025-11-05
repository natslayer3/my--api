from flask import Flask, jsonify, request, abort
import os
import psycopg2
import time

app = Flask(__name__)

# ==========================
# 🔹 In-memory News Section
# ==========================

# In-memory store
news = [
    {"id": 1, "title": "Initial News", "content": "This is the first article."}
]

# Simple auto-increment for IDs
next_id = 2


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "Welcome to the News API!",
        "endpoints": {
            "list_all_news": "GET /news",
            "create_news": "POST /news",
            "update_news": "PUT /news/<id>",
            "delete_news": "DELETE /news/<id>",
            "database_health": "GET /db-health"
        }
    })


@app.route("/news", methods=["GET"])
def list_news():
    return jsonify({"count": len(news), "items": news})


@app.route("/news", methods=["POST"])
def create_news():
    global next_id
    if not request.json or 'title' not in request.json:
        abort(400)  # Bad request

    new_item = {
        'id': next_id,
        'title': request.json['title'],
        'content': request.json.get('content', "")
    }
    news.append(new_item)
    next_id += 1
    return jsonify(new_item), 201  # Created


# Helper function to find an item by ID
def find_news_item(item_id):
    for item in news:
        if item['id'] == item_id:
            return item
    return None


@app.route("/news/<int:item_id>", methods=["PUT"])
def update_news(item_id: int):
    item = find_news_item(item_id)
    if not item:
        abort(404)  # Not found
    if not request.json:
        abort(400)

    # Update fields
    if 'title' in request.json:
        item['title'] = request.json['title']
    if 'content' in request.json:
        item['content'] = request.json['content']

    return jsonify(item)


@app.route("/news/<int:item_id>", methods=["DELETE"])
def delete_news(item_id: int):
    item = find_news_item(item_id)
    if not item:
        abort(404)

    news.remove(item)
    return jsonify({"status": "deleted", "id": item_id})


# ==========================
# 🔹 PostgreSQL Health Check
# ==========================

def get_db_connection():
    db_host = os.environ.get('DB_HOST')
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')

    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_pass
            )
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            app.logger.warning("Database not ready, retrying...")
            time.sleep(5)

    app.logger.error("Could not connect to database.")
    return None


@app.route("/db-health", methods=["GET"])
def db_health_check():
    conn = get_db_connection()
    if conn is None:
        return jsonify({
            "status": "error",
            "message": "Database connection failed"
        }), 500

    conn.close()
    return jsonify({
        "status": "ok",
        "message": "Database connection successful"
    })


# ==========================
# 🔹 Main
# ==========================

if __name__ == "__main__":
    print("🚀 Running News API with DB Health Check...")
    app.run(threaded=True, host='0.0.0.0', port=3000, debug=True)
