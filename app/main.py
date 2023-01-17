import hmac
import logging
import os
import json

from tinydb import TinyDB
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, status

load_dotenv()

SECRET = os.environ.get("CPWEBHOOK_SECRET") or "secret_key"
X_SIG = "x-cp-signature"
DB_PATH = os.environ.get("CPWEBHOOK_DB_PATH") or "data"

logger = logging.getLogger("uvicorn")
logger.info("Secret Key is %s", SECRET)

app = FastAPI(debug=True)

table = None

@app.on_event("startup")
async def database():
    global table
    os.makedirs(DB_PATH)
    db = TinyDB(DB_PATH + "/data.json")  # create a new database named "data"
    table = db.table('messages')

def create_hash(key, message):
    h = hmac.new(key=key.encode('utf-8'), msg=message, digestmod="sha256")
    message_digest = h.hexdigest()
    return message_digest

def add_message(msg):
    table.insert(json.loads(msg))

@app.get("/messages", status_code=200)
async def messages():
    return table.all()

@app.post("/", status_code=403)
async def root(request: Request, response: Response):
    msg_body = await request.body()
    logger.info("Body: %s", msg_body)
    logger.info("Headers: %s", request.headers)

    xsig = request.headers.get(X_SIG)
    sig = create_hash(SECRET, msg_body)

    logger.info("xsig: %s", xsig)
    logger.info("sig: %s", sig)

    if xsig == sig:
        response.status_code = status.HTTP_200_OK
        add_message(msg_body.decode("utf8"))
        return {"status": "OK"}
    
    return {"status": "failed"}