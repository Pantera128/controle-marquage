import streamlit as st
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from pyzbar.pyzbar import decode
import tempfile

st.set_page_config(page_title="Contrôle Marquage", layout="centered")

st.title("📋 Contrôle calque de marquage")
st.write("Vérifie automatiquement la cohérence entre une photo d’Ordre de Fabrication et un fichier PDF de marquage.")

# === Upload ===
uploaded_photo = st.file_uploader("📷 Photo de l'Ordre de Fabrication (image)", type=["png", "jpg", "jpeg"])
uploaded_pdf = st.file_uploader("📄 PDF du marquage", type=["pdf"])

def extraire_infos(text):
    def extract(label):
        for line in text.splitlines():
            if label in line.upper():
                return line.split(":")[-1].strip()
        return "❌ Non trouvé"
    
    return {
        "ref_client": extract("REF CLIENT"),
        "lot": extract("LOT"),
        "date": extract("DATE"),
    }

def lire_datamatrix(image):
    codes = decode(image)
    for code in codes:
        if code.type == "DATAMATRIX":
            return code.data.decode("utf-8")
    return None

if uploaded_photo and uploaded_pdf:
    st.subheader("🔍 Résultats du contrôle")

    with tempfile.NamedTemporaryFile(delete=False) as temp_img:
        temp_img.write(uploaded_photo.read())
        image = Image.open(temp_img.name)
        text_of = pytesseract.image_to_string(image, lang="fra")
        infos_of = extraire_infos(text_of)

    with tempfile.NamedTemporaryFile(delete=False) as temp_pdf:
        temp_pdf.write(uploaded_pdf.read())
        doc = fitz.open(temp_pdf.name)
        text_pdf = "".join([page.get_text() for page in doc])
        infos_pdf = extraire_infos(text_pdf)

    # Lecture datamatrix
    datamatrix = lire_datamatrix(image)

    # Comparaison
    for key in infos_of:
        val_of = infos_of[key]
        val_pdf = infos_pdf[key]
        if val_of == val_pdf:
            st.success(f"✅ {key.upper()} correspond : {val_of}")
        else:
            st.error(f"❌ {key.upper()} différent ! OF = {val_of} / PDF = {val_pdf}")

    if datamatrix:
        st.info(f"📦 Datamatrix détecté : `{datamatrix}`")
        if infos_of["lot"] in datamatrix and infos_of["date"] in datamatrix:
            st.success("✅ Datamatrix contient bien le numéro de lot et la date.")
        else:
            st.warning("⚠️ Le datamatrix ne correspond pas aux données extraites.")
    else:
        st.warning("⚠️ Aucun datamatrix détecté dans la photo.")

