import hmac
import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, status

load_dotenv()
SECRET = os.environ.get("CPWEBHOOK_SECRET") or "secret_key"
X_SIG = "x-cp-signature"

app = FastAPI(debug=True)

logger = logging.getLogger("uvicorn")

logger.info("Secret Key is %s", SECRET)

def create_hash(key, message):
    h = hmac.new(key=key.encode('utf-8'), msg=message, digestmod="sha256")
    message_digest = h.hexdigest()
    return message_digest

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
        return {"status": "OK"}
    
    return {"status": "failed"}