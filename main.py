import requests
from fastapi import FastAPI, HTTPException
from PyPDF2 import PdfReader

app = FastAPI()

@app.post('/extract_text')
async def extract_text(url: str, numOfPage: int = 1):
    # Download the PDF file
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to download PDF")

    with open('temp.pdf', 'wb') as f:
        f.write(response.content)

    # Open the PDF file and extract text and images
    with open('temp.pdf', 'rb') as f:
        reader = PdfReader(f)
        if 0 <= numOfPage <= len(reader.pages) - 1:
            page_obj = reader.pages[numOfPage]
            print(page_obj)
            text = page_obj.extract_text()
            images = page_obj.extract_images()
        else:
            text = ''
            images = []

    # Delete the temporary PDF file
    # Comment out the following line if you want to keep the downloaded file
    import os
    os.remove('temp.pdf')

    return {'text': text, 'numberOfPages': len(reader.pages), 'images': images}
