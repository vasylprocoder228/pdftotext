import requests
from fastapi import FastAPI
from fastapi import HTTPException
from PyPDF2 import PdfReader
import fitz
import os
from PIL import Image
import base64

app = FastAPI()

@app.post('/extract_text')
async def extract_text(pdf_url: str):
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
        base_list.append({"imageName":image_name,"base64":base64_image})
    return("images", base_list)
