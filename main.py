import requests
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Body
from fastapi import FastAPI, HTTPException
import json

app = FastAPI()

@app.post('/extract_text')
@app.post("/extract_text")
async def call_dp_login_api():
    url = "https://dubaiproperties.my.site.com/services/apexrest/DPLogin"
    headers = {'Content-Type': 'application/json'}
@@ -17,11 +15,6 @@ async def call_dp_login_api():

    response = requests.post(url, headers=headers, data=json.dumps(body))

    # Always good to print out the status code for debugging
    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        return None

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="API request failed")
    return response.json()
