import json, os, logging
from datetime import datetime
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobBlock
import uuid, base64

CONN_STR = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
CONTAINER = "vidhuk-logs"
BLOB_NAME = "vidhuk.jsonl"

def main(req: func.HttpRequest) -> func.HttpResponse:
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    if req.method == "OPTIONS":
        return func.HttpResponse("", status_code=200, headers=headers)

    try:
        body = req.get_json()
        text = (body.get("text") or "").strip()
        if not text:
            return func.HttpResponse("empty", status_code=400, headers=headers)

        entry = {
            "ts": body.get("ts") or datetime.utcnow().isoformat(),
            "pritcha": body.get("pritcha", ""),
            "text": text
        }
        line = json.dumps(entry, ensure_ascii=False) + "\n"

        if CONN_STR:
            try:
                client = BlobServiceClient.from_connection_string(CONN_STR)
                container = client.get_container_client(CONTAINER)
                try:
                    container.create_container()
                except:
                    pass
                blob = container.get_blob_client(BLOB_NAME)
                # Append через block list
                try:
                    existing = blob.download_blob().readall().decode("utf-8")
                except:
                    existing = ""
                blob.upload_blob((existing + line).encode("utf-8"), overwrite=True)
            except Exception as e:
                logging.error(f"blob error: {e}")

        return func.HttpResponse(
            json.dumps({"ok": True}),
            status_code=200,
            mimetype="application/json",
            headers=headers
        )

    except Exception as e:
        logging.error(e)
        return func.HttpResponse("error", status_code=500, headers=headers)
