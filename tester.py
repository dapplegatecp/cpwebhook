import hmac
import sys
import os

import requests
from dotenv import load_dotenv

load_dotenv()
SECRET = os.environ.get("CPWEBHOOK_SECRET") or "secret_key"
X_SIG = "x-cp-signature"
URL = os.environ.get("CPWEBHOOK_URL") or "http://localhost:8000"

def create_hash(key, message):
    h = hmac.new(key=key.encode('utf-8'), msg=message, digestmod="sha256")
    message_digest = h.hexdigest()
    return message_digest

if __name__ == "__main__":
    data = "".join(sys.stdin.readlines()).encode('utf-8')
    h = create_hash(SECRET, data)
    headers = {X_SIG:h}
    r = requests.post(URL, headers=headers, data=data)
    print("r.status_code: %s" % r.status_code)
    print(r.text)