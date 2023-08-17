import requests
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Body
import json

app = FastAPI()

@app.post('/extract_text')
async def call_dp_login_api():
    url = "https://dubaiproperties.my.site.com/services/apexrest/DPLogin"
    headers = {'Content-Type': 'application/json'}
    body = {
        "SFusername":"eloquaintegrationuser@dpg.com.prod",
        "SFpassword":"sfmcdp2022vWl88ybT0rO8jgRTQ5edwpSU"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(body))

    # Always good to print out the status code for debugging
    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    else:
        return None
    
