import requests
import fitz
from fastapi import FastAPI
from fastapi import HTTPException

app = FastAPI()

@app.post('/extract_html')
async def extract_html(url: str):
    # Download the PDF file
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to download PDF")

    with open('temp.pdf', 'wb') as f:
        f.write(response.content)

    # Open the PDF file and extract HTML content
    html = ''
    with fitz.open('temp.pdf') as doc:
        for page in doc:
            html += page.get_text("html")

    # Delete the temporary PDF file
    # Comment out the following line if you want to keep the downloaded file
    import os
    os.remove('temp.pdf')

    return {'html': html}
