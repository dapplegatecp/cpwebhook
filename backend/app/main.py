import hmac
import json
import logging
import os

from sse_starlette import EventSourceResponse
import motor.motor_asyncio
from pymongo.cursor import CursorType
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

SECRET = os.environ.get("CPWEBHOOK_SECRET") or "secret_key"
X_SIG = "x-cp-signature"

logger = logging.getLogger("uvicorn")
logger.info("Secret Key is %s", SECRET)

app = FastAPI(debug=True)

origins = [
    "https://www.webhook.app.crdlpt.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = None


@app.on_event("startup")
async def database():
    global db
    mongo_user = os.environ.get("CPWEBHOOK_DB_USER") or "root"
    mongo_pw = os.environ.get("CPWEBHOOOK_DB_PASS") or "example"
    mongo_host = os.environ.get("CPWEBHOOK_DB_HOST") or "localhost"
    mongo_url = f"mongodb://{mongo_user}:{mongo_pw}@{mongo_host}/?authSource=admin"
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
    db = client.webhooks


def create_hash(key, message):
    h = hmac.new(key=key.encode('utf-8'), msg=message, digestmod="sha256")
    message_digest = h.hexdigest()
    return message_digest


async def add_message(msg):
    # modify data a bit
    data = msg['data'][0]
    info = data.pop('info')
    data['destination_config_id'] = info.get("destination_config_id")
    data['message'] = info.get('message') or info.get('msg')
    router_details = data.pop('router_details', None)
    if router_details:
        data['router_name'] = router_details.get('name')
        data['router_description'] = router_details.get('description')
        data['router_mac'] = router_details.get('mac')
        data['router_serial_number'] = router_details.get('serial_number')
        data['router_asset_id'] = router_details.get('asset_id')
        data['router_custom1'] = router_details.get('custom1')
        data['router_custom2'] = router_details.get('custom2')
    await db.alerts.insert_one(data)


@app.get("/messages", status_code=status.HTTP_200_OK)
async def messages():
    rval = []
    async for m in db.alerts.find({}):
        m['_id'] = str(m['_id'])
        rval.append(m)
    return rval


@app.get('/stream', status_code=status.HTTP_200_OK)
async def stream():
    async def stream_data():
        cursor = db.alerts.find({},cursor_type=CursorType.TAILABLE_AWAIT)
        while cursor.alive:
            async for m in cursor:
                m['_id'] = str(m['_id'])
                yield json.dumps(m)
    return EventSourceResponse(stream_data())


@app.post("/messages", status_code=403)
async def root(request: Request, response: Response):
    msg_body = await request.body()
    logger.info("Body: %s", msg_body)
    logger.info("Headers: %s", request.headers)

    xsig = request.headers.get(X_SIG)
    sig = create_hash(SECRET, msg_body)

    logger.info("xsig: %s", xsig)
    logger.info("sig: %s", sig)

    if xsig == sig:
        try:
            msg = json.loads(msg_body.decode("utf8"))
        except ValueError as e:
            logger.exception(e)
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"status": "bad request"}
        response.status_code = status.HTTP_200_OK
        await add_message(msg)
        return {"status": "OK"}
    
    return {"status": "forbidden"}