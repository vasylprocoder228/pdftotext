import easyocr
import fitz
import os
import io
from PIL import Image
import base64
import requests
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Body
from PyPDF2 import PdfReader
import numpy as np
import networkx as nx
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

@app.post('/extract_text')
async def extract_text(pdf_url: str):
    response = requests.get(pdf_url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to download PDF")
    with open('temp.pdf', 'wb') as f:
        f.write(response.content)
    # Open the PDF file and extract text
    with open('temp.pdf', 'rb') as f:
        reader = PdfReader(f)
        num_pages = len(reader.pages)
        text = ''
        for page in range(num_pages):
            page_obj = reader.pages[page]
            text += page_obj.extract_text()
    os.remove('temp.pdf')
    return {'text': text}

@app.post('/extract_text_from_blob')    
async def process_file(base64_content: str = Body(...)):
    file_bytes = base64.b64decode(base64_content)
    if is_pdf(file_bytes):
        return extract_text_from_pdf_blob(file_bytes)
    else:
        text_from_image = extract_text_from_base64(file_bytes)
        return {'text': text_from_image}

@app.post('/extract_files')
async def extract_files(pdf_url: str):
    # Step 2: Download the PDF file
    response = requests.get(pdf_url)
    pdf_bytes = response.content
    pdf_file = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_nums = len(pdf_file)
    images_list = []
    base_list = []
    totalLen = 0
    for page_num in range(page_nums):
        page_content = pdf_file[page_num]
        images_list.extend(page_content.get_images())
    for i, image in enumerate(images_list, start=1):
        xref = image[0]
        base_image = pdf_file.extract_image(xref)
        image_bytes = base_image['image']
        image_ext = base_image['ext']
        image_name = str(i) + '.' + image_ext
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        base_list.append({"imageName": image_name, "base64": base64_image})
    return("images", base_list)

def extract_text_from_pdf_blob(pdf_bytes):
    try:
        with io.BytesIO(pdf_bytes) as f:
            reader = PdfReader(f)
            num_pages = len(reader.pages)
            text = ''
            for page in range(num_pages):
                page_obj = reader.pages[page]
                text += page_obj.extract_text()
    except binascii.Error:
        raise HTTPException(status_code=400, detail="Invalid base64 format")
    return {'text': text}

def is_pdf(file_bytes):
    pdf_signature = b'%PDF'
    return file_bytes.startswith(pdf_signature)

def extract_text_from_base64(base64_bytes):
    # Convert bytes data to a PIL image
    image = Image.open(io.BytesIO(base64_bytes))
    
    # Convert PIL image to numpy array
    image_np = np.array(image)
    
    # Initialize the OCR reader
    reader = easyocr.Reader(['en'])
    
    # Read text from the image
    result = reader.readtext(image_np, detail=0)
    
    # Return the extracted text as a single string
    return "".join(result)

    
