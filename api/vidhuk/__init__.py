import json
import os
import logging
import azure.functions as func
from datetime import datetime

LOG_PATH = os.getenv("VIDHUK_LOG_PATH", "C:/inin/logs/vidhuk.jsonl")

def main(req: func.HttpRequest) -> func.HttpResponse:
    # CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=200, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        })

    try:
        body = req.get_json()
        entry = {
            "ts": body.get("ts") or datetime.utcnow().isoformat(),
            "pritcha": body.get("pritcha", ""),
            "text": body.get("text", "").strip()
        }

        if not entry["text"]:
            return func.HttpResponse("empty", status_code=400)

        # Локальний лог
        try:
            os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logging.warning(f"local log failed: {e}")

        return func.HttpResponse(
            json.dumps({"ok": True}),
            status_code=200,
            mimetype="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )

    except Exception as e:
        logging.error(e)
        return func.HttpResponse("error", status_code=500)
