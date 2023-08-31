import requests
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Body
from fastapi import FastAPI, HTTPException
import os.path
import base64
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

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="API request failed")
    return response.json()
    
@app.post('/extract_blob_extention')
async def get_file_details(url: str):
    response = requests.get(url)
    file_content = response.content
    file_extension = os.path.splitext(url)[1]

    base64_content = base64.b64encode(file_content).decode('utf-8')

    file_details = {
        'base64': base64_content,
        'extension': file_extension
    }

    return file_details
