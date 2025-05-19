import streamlit as st
from PIL import Image
import fitz  # PyMuPDF

# Imports désactivés (commentés) pour la reconnaissance OCR et Datamatrix
# from pylibdmtx.pylibdmtx import decode as decode_datamatrix
# import pytesseract

def extract_text(image):
    # Désactivation temporaire : on ne fait rien et on retourne une chaîne vide
    return ""

def decode_datamatrix(image):
    # Désactivation temporaire : on ne détecte aucun datamatrix
    return []

def load_pdf_page_as_image(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

st.title("Contrôle de marquage (version simplifiée)")

uploaded_pdf = st.file_uploader("Importer un fichier PDF de marquage", type=["pdf"])
uploaded_img = st.file_uploader("Importer une capture d'écran de l'OF (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_pdf:
    img_pdf = load_pdf_page_as_image(uploaded_pdf)
    st.image(img_pdf, caption="Page PDF chargée", use_column_width=True)
    text_pdf = extract_text(img_pdf)  # vide pour l'instant
    st.write("Texte extrait du PDF (désactivé):", text_pdf)

if uploaded_img:
    img_of = Image.open(uploaded_img)
    st.image(img_of, caption="Image OF chargée", use_column_width=True)
    text_of = extract_text(img_of)  # vide pour l'instant
    st.write("Texte extrait de l'OF (désactivé):", text_of)

# Ici tu pourras ajouter plus tard la comparaison entre les textes ou autres contrôles

st.info("La reconnaissance OCR et datamatrix est désactivée temporairement pour éviter les erreurs liées à l'environnement Streamlit Cloud.")

