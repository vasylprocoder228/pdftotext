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
async def extract_text(url: str):
    pdf_url = "https://rhaindubai.com/wp-content/uploads/2023/02/FOOD-MENU-RHAIN.pdf"
    # Step 2: Download the PDF file
    response = requests.get(pdf_url)
    pdf_bytes = response.content
    pdf_file = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_nums = len(pdf_file)
    images_list = []
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
        print("Base64 image size:", len(base64_image))
        totalLen += len(base64_image)
    return("Total Length", totalLen)
