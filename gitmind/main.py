import os
import sys
import time
from datetime import datetime
from functools import wraps
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from gitmind.api.gitlab_client import GitLabClient
from gitmind.webhooks.handler import WebhookHandler, sanitize_secrets
from gitmind.config import GITLAB_CONFIG, GROQ_CONFIG
from gitmind.feedback import get_feedback_storage
from gitmind.learning import get_learning_engine
from gitmind.logging_config import setup_logging, get_logger
from gitmind.monitoring import init_sentry

setup_logging()
logger = get_logger(__name__)

init_sentry()

app = Flask(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per minute"],
    storage_uri="memory://"
)

start_time = time.time()

gitlab_token = os.environ.get("GITLAB_TOKEN", "")
secret_token = os.environ.get("GITLAB_WEBHOOK_SECRET", "")

gitlab_client = GitLabClient(token=gitlab_token, gitlab_url=GITLAB_CONFIG["gitlab_url"])

from qbrain.llm.groq_client import GroqClient
llm_client = GroqClient(api_key=GROQ_CONFIG["api_key"], model=GROQ_CONFIG["model"])
webhook_handler = WebhookHandler(gitlab_client, llm_client, secret_token)
feedback_storage = get_feedback_storage()
learning_engine = get_learning_engine()


@app.route("/")
def index():
    return jsonify({
        "name": "GitMind - AI Assistant for GitLab",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook",
            "health": "/health",
            "review": "/api/review",
        }
    })


@app.route("/health")
def health():
    import time
    import psutil
    
    checks = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }
    
    try:
        process = psutil.Process()
        checks["memory_mb"] = process.memory_info().rss / 1024 / 1024
        checks["cpu_percent"] = process.cpu_percent(0.1)
    except:
        checks["memory_mb"] = None
        checks["cpu_percent"] = None
    
    try:
        feedback_count = len(feedback_storage.reviews)
        checks["total_reviews"] = feedback_count
    except:
        checks["total_reviews"] = 0
    
    all_healthy = all(v is not None and v != "error" for k, v in checks.items() if k not in ["status", "timestamp"])
    
    if not all_healthy:
        checks["status"] = "degraded"
        return jsonify(checks), 503
    
    return jsonify(checks)


@app.route("/webhook", methods=["POST"])
def webhook():
    event_type = request.headers.get("X-Gitlab-Event", "")
    
    if secret_token:
        token = request.headers.get("X-Gitlab-Token", "")
        if token != secret_token:
            return jsonify({"error": "Unauthorized"}), 401
    
    payload = request.json
    
    event_type_map = {
        "merge_request_hook": "merge_request",
        "issue_hook": "issue",
        "note_hook": "note",
        "push_hook": "push",
    }
    
    event_key = event_type.lower().replace(" ", "_")
    event_key = event_type_map.get(event_key, event_key.replace("_hook", "").replace("_hook", ""))
    
    result = webhook_handler.handle(event_key, payload)
    
    return jsonify(result)


@app.route("/api/review", methods=["POST"])
@limiter.limit("10 per minute")
def api_review():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400
    except Exception:
        return jsonify({"error": "Invalid request format"}), 400
    
    project_id = data.get("project_id")
    mr_iid = data.get("mr_iid")
    
    if not project_id or not mr_iid:
        return jsonify({"error": "Missing project_id or mr_iid"}), 400
    
    try:
        project_id = int(project_id)
        mr_iid = int(mr_iid)
    except (ValueError, TypeError):
        return jsonify({"error": "project_id and mr_iid must be integers"}), 400
    
    try:
        result = webhook_handler.process_mr_review(project_id, mr_iid)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Review failed: {str(e)}"}), 500


@app.route("/api/issue", methods=["POST"])
def api_issue():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400
    except Exception:
        return jsonify({"error": "Invalid request format"}), 400
    
    project_id = data.get("project_id")
    issue_iid = data.get("issue_iid")
    
    if not project_id or not issue_iid:
        return jsonify({"error": "Missing project_id or issue_iid"}), 400
    
    try:
        project_id = int(project_id)
        issue_iid = int(issue_iid)
    except (ValueError, TypeError):
        return jsonify({"error": "project_id and issue_iid must be integers"}), 400
    
    try:
        result = webhook_handler.process_issue_response(project_id, issue_iid)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Issue response failed: {str(e)}"}), 500


@app.route("/api/chat", methods=["POST"])
@limiter.limit("5 per minute")
def api_chat():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400
    except Exception:
        return jsonify({"error": "Invalid request format"}), 400
    
    message = data.get("message")
    
    if not message:
        return jsonify({"error": "Missing message"}), 400
    
    try:
        response = llm_client.generate(message)
        sanitized = sanitize_secrets(response.get("content", ""))
        return jsonify({
            "response": sanitized,
            "success": response.get("success", False)
        })
    except Exception as e:
        return jsonify({"error": f"Chat failed: {str(e)}"}), 500


@app.route("/api/feedback/stats", methods=["GET"])
def api_feedback_stats():
    stats = feedback_storage.get_stats()
    analysis = learning_engine.analyze_performance()
    return jsonify({
        "stats": stats,
        "analysis": analysis
    })


@app.route("/api/feedback/recent", methods=["GET"])
def api_feedback_recent():
    n = request.args.get("n", 10, type=int)
    recent = feedback_storage.get_recent(n)
    return jsonify({"recent": recent})


@app.route("/api/feedback/helpful", methods=["POST"])
def api_feedback_helpful():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400
    except Exception:
        return jsonify({"error": "Invalid request format"}), 400
    
    mr_iid = data.get("mr_iid")
    project_id = data.get("project_id")
    
    if not mr_iid or not project_id:
        return jsonify({"error": "Missing mr_iid or project_id"}), 400
    
    try:
        mr_iid = int(mr_iid)
        project_id = int(project_id)
    except (ValueError, TypeError):
        return jsonify({"error": "mr_iid and project_id must be integers"}), 400
    
    success = feedback_storage.mark_helpful(mr_iid, project_id, True)
    stats = learning_engine.get_stats_summary()
    
    return jsonify({
        "success": success,
        "marked": "helpful",
        "message": stats
    })


@app.route("/api/feedback/not-helpful", methods=["POST"])
def api_feedback_not_helpful():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON body"}), 400
    except Exception:
        return jsonify({"error": "Invalid request format"}), 400
    
    mr_iid = data.get("mr_iid")
    project_id = data.get("project_id")
    
    if not mr_iid or not project_id:
        return jsonify({"error": "Missing mr_iid or project_id"}), 400
    
    try:
        mr_iid = int(mr_iid)
        project_id = int(project_id)
    except (ValueError, TypeError):
        return jsonify({"error": "mr_iid and project_id must be integers"}), 400
    
    success = feedback_storage.mark_helpful(mr_iid, project_id, False)
    stats = learning_engine.get_stats_summary()
    
    return jsonify({
        "success": success,
        "marked": "not_helpful",
        "message": stats
    })


@app.route("/api/feedback/tips", methods=["GET"])
def api_feedback_tips():
    tips = learning_engine.get_tips_for_reviewer()
    return jsonify({"tips": tips})


@app.route("/api/learning/status", methods=["GET"])
def api_learning_status():
    status = learning_engine.get_learning_status()
    return jsonify(status)


@app.route("/api/learning/summary", methods=["GET"])
def api_learning_summary():
    summary = learning_engine.get_stats_summary()
    return jsonify({"summary": summary})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
