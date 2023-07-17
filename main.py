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
import nltk
import spacy
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
from pydantic import BaseModel

app = FastAPI()
nltk.download('punkt')
nltk.download('stopwords')

class Request(BaseModel):
    textToFormat: str

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
    
def extract_text_from_image(base64_image):
    # Decode the Base64 image
    decoded_image = base64.b64decode(base64_image)
    
    # Open the image using PIL
    image = Image.open(io.BytesIO(decoded_image))
    
    # Perform OCR using pytesseract
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text
    
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
        base_list.append({"imageName": image_name, "base64": base64_image})
    return("images", base_list)
    
@app.post('/generate_data')
async def extract_text(req: Request):
    summary = generate_summary(req.textToFormat)
    return { "formattedText" : summary }
    
def read_article(text):
    # Split the text into sentences
    sentences = sent_tokenize(text)
    return sentences

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []

    # Convert sentences to lowercase and tokenize them
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    # Remove stopwords from sentences
    sent1 = [w for w in sent1 if w not in stopwords]
    sent2 = [w for w in sent2 if w not in stopwords]

    # Calculate sentence similarity using cosine distance
    all_words = list(set(sent1 + sent2))
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # Build term frequency vectors
    for w in sent1:
        vector1[all_words.index(w)] += 1

    for w in sent2:
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)


def build_similarity_matrix(sentences, stopwords):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                similarity_matrix[i][j] = sentence_similarity(sentences[i], sentences[j], stopwords)

    return similarity_matrix


def extract_keywords(text):
    # Load spaCy model
    nlp = spacy.load('en_core_web_sm')

    # Tokenize text into sentences
    sentences = sent_tokenize(text)

    # Extract entities from each sentence
    keywords = []
    for sentence in sentences:
        doc = nlp(sentence)
        entities = [entity.text for entity in doc.ents if entity.label_ in ['QUANTITY', 'DATE', 'CARDINAL', 'MONEY']]
        keywords.extend(entities)

    return keywords


def generate_summary(text):
    # Read the text and tokenize it into sentences
    sentences = read_article(text)

    # Remove stopwords from sentences
    stop_words = stopwords.words('english')
    sentence_similarity_matrix = build_similarity_matrix(sentences, stop_words)

    # Use PageRank algorithm to rank sentences
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_matrix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Set the number of summary sentences based on the number of sentences in the text
    num_summary_sentences = min(3, len(sentences))

    # Extract keywords from the text
    keywords = extract_keywords(text)

    # Identify sentences containing keywords
    keyword_sentences = []
    if keywords:
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                keyword_sentences.append(sentence)

    # Sort the sentences based on their scores
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)

    # Select the top 'num_summary_sentences' sentences as the summary
    summary_sentences = [s for _, s in ranked_sentences[:num_summary_sentences]]

    # Include keyword sentences in the summary
    summary_sentences += keyword_sentences

    summary = ' '.join(summary_sentences)
    return summary
