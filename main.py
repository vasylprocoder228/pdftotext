import fitz
import os
from PIL import Image
import requests
import base64
from fastapi import FastAPI

app = FastAPI()

@app.get('/convert-pdf-to-base64')
async def convert_pdf_to_base64():
    pdf_url = "https://www.meraas.com/en/-/mediadh/project/meraasecosystem/meraas/real-estate/central-park-thyme/finalcp_brochure-english_thyme.pdf"
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

    result = []
    for i, image in enumerate(images_list, start=1):
        xref = image[0]
        base_image = pdf_file.extract_image(xref)
        image_bytes = base_image['image']
        image_ext = base_image['ext']
        image_name = str(i) + '.' + image_ext
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        result.append({
            'image_name': image_name,
            'base64_image': base64_image,
            'base64_image_size': len(base64_image)
        })
        totalLen += len(base64_image)

    return {
        'total_length': totalLen,
        'images': result
    }
