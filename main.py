import requests
from fastapi import FastAPI, HTTPException
import json

app = FastAPI()

@app.post("/extract_text")
async def call_dp_login_api():
    url = "https://dubaiproperties.my.site.com/services/apexrest/DPLogin"
    headers = {'Content-Type': 'application/json'}
    body = {
        "SFusername":"eloquaintegrationuser@dpg.com.prod",
        "SFpassword":"sfmcdp2022vWl88ybT0rO8jgRTQ5edwpSU"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(body))

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="API request failed")
    return response.json()
