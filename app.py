import streamlit as st
from PIL import Image
import io
import requests
import fitz  # PyMuPDF

API_KEY = "helloworld"  # clé gratuite OCR.space

def pdf_to_image(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

def ocr_space_image(image: Image.Image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    response = requests.post(
        "https://api.ocr.space/parse/image",
        files={"filename": ("image.png", img_bytes)},
        data={"apikey": API_KEY, "language": "fra", "isOverlayRequired": False}
    )
    result = response.json()
    if result.get("IsErroredOnProcessing"):
        st.error("Erreur OCR: " + result.get("ErrorMessage")[0])
        return ""
    parsed_text = result.get("ParsedResults")[0].get("ParsedText")
    return parsed_text

st.title("Contrôle de marquage avec OCR via OCR.space")

uploaded_pdf = st.file_uploader("Importer un PDF de marquage", type=["pdf"])
uploaded_img = st.file_uploader("Importer une capture d'écran de l'OF", type=["png", "jpg", "jpeg"])

if uploaded_pdf:
    img_pdf = pdf_to_image(uploaded_pdf)
    st.image(img_pdf, caption="Page PDF chargée", use_container_width=True)
    text_pdf = ocr_space_image(img_pdf)
    st.text_area("Texte OCR extrait du PDF", text_pdf, height=300)

if uploaded_img:
    img_of = Image.open(uploaded_img)
    st.image(img_of, caption="Image OF chargée", use_container_width=True)
    text_of = ocr_space_image(img_of)
    st.text_area("Texte OCR extrait de l'OF", text_of, height=300)

st.info("L'OCR est réalisé via le service OCR.space (gratuit, avec limite de requêtes).")
