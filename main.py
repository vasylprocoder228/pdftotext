import requests
from fastapi import FastAPI
from fastapi import HTTPException
from PyPDF2 import PdfReader

app = FastAPI()

@app.post('/extract_text')
async def extract_text(url: str):
    # Download the PDF file
    response = requests.get(url)
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
    import os
    os.remove('temp.pdf')

    return {'text': text}
