import fitz
import os
import io
from PIL import Image
import base64
import requests
from fastapi import FastAPI
from fastapi import HTTPException
from PyPDF2 import PdfReader
import pytesseract

app = FastAPI()

@app.post('/extract_text')
async def extract_text(pdf_url: str):
    # Download the PDF file
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

    # Delete the temporary PDF file
    # Comment out the following line if you want to keep the downloaded file
    os.remove('temp.pdf')

    return {'text': text}
def extract_text_from_image(img):
    pil_img = Image.open(io.BytesIO(img))
    text = pytesseract.image_to_string(pil_img)
    return text
@app.post('/extract_files')
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
        text = extract_text_from_image(image_bytes)
        base_list.append({"imageName": image_name, "text": text})
    return("images", base_list)
