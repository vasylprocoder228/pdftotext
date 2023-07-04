import requests
import io
import pdf2image
import pytesseract
from PIL import Image
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post('/extract_text')
async def extract_text(url: str, numOfPage: int = 1):
    # Download the PDF file
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to download PDF")

    with open('temp.pdf', 'wb') as f:
        f.write(response.content)

    # Convert PDF pages to images
    images = pdf2image.convert_from_path('temp.pdf')

    # Extract text from the specified page
    if 0 <= numOfPage <= len(images) - 1:
        image = images[numOfPage]
        image_data = io.BytesIO()
        image.save(image_data, format='PNG')
        image_data.seek(0)
        extracted_text = pytesseract.image_to_string(Image.open(image_data))
    else:
        extracted_text = ''

    # Convert extracted text to HTML
    extracted_html = extracted_text.replace('\n', '<br>')

    # Delete the temporary PDF file
    # Comment out the following line if you want to keep the downloaded file
    import os
    os.remove('temp.pdf')

    return {
        'text': extracted_text,
        'html': extracted_html,
        'numberOfPages': len(images)
    }
