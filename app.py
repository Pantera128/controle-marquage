import streamlit as st
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import cv2
import numpy as np
from pdf2image import convert_from_bytes

st.title("🧐 Contrôle de calque de marquage")

uploaded_pdf = st.file_uploader("📄 Upload du fichier PDF de marquage", type="pdf")
uploaded_of = st.file_uploader("📸 Upload de la photo de l’Ordre de Fabrication (OF)", type=["png", "jpg", "jpeg"])

if uploaded_pdf and uploaded_of:
    st.success("Fichiers bien reçus 👍")

    # Convertir la première page du PDF en image
    pdf_images = convert_from_bytes(uploaded_pdf.read())
    pdf_image = pdf_images[0]
    pdf_text = pytesseract.image_to_string(pdf_image)

    # Lire la photo OF
    of_image_pil = Image.open(uploaded_of).convert("RGB")
    of_text = pytesseract.image_to_string(of_image_pil)

    # Affichage debug
    st.subheader("🔍 Texte extrait du PDF de marquage")
    st.text(pdf_text)

    st.subheader("🔍 Texte extrait de la photo de l'OF")
    st.text(of_text)

    # Analyse QR/Datamatrix avec OpenCV
    st.subheader("📦 Contenu du Datamatrix détecté")

    of_np = np.array(of_image_pil)
    gray = cv2.cvtColor(of_np, cv2.COLOR_RGB2GRAY)

    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(gray)

    if data:
        st.code(data, language="text")
    else:
        st.warning("⚠️ Aucun QR Code / Datamatrix détecté sur l'image de l'OF.")

    # Vérifications simples
    ref_client_ok = "REF CLIENT" in pdf_text and "REF CLIENT" in of_text
    lot_ok = "lot" in pdf_text.lower() and "lot" in of_text.lower()
    date_ok = "date" in pdf_text.lower() and "date" in of_text.lower()

    st.subheader("✅ Vérification automatique")
    st.write(f"Réf client détectée : {'✅' if ref_client_ok else '❌'}")
    st.write(f"N° de lot détecté : {'✅' if lot_ok else '❌'}")
    st.write(f"Date détectée : {'✅' if date_ok else '❌'}")

else:
    st.info("📥 Merci d’importer le PDF de marquage **et** la photo de l’OF.")
