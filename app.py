from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve
import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv
import fitz  # PyMuPDF
from io import BytesIO

load_dotenv()

app = Flask(__name__)
CORS(app)

# پیکربندی کلید Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# مدل مورد استفاده
model = genai.GenerativeModel("gemini-1.5-flash")

# URL فایل PDF در GitHub (خام)
PDF_GITHUB_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/BRANCH/PATH_TO_PDF.pdf"

def extract_text_from_pdf_from_url(url):
    """دانلود و استخراج متن PDF از GitHub"""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("خطا در دانلود PDF از GitHub")
    
    file_like = BytesIO(response.content)
    doc = fitz.open(stream=file_like, filetype="pdf")
    
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        user_msg = request.form.get("message", "")
        if not user_msg:
            return jsonify({"error": "No message provided"}), 400

        pdf_text = extract_text_from_pdf_from_url(PDF_GITHUB_URL)
        if not pdf_text:
            return jsonify({"error": "Failed to extract text from PDF."}), 500

        prompt = f"""
        محتوای فایل PDF به شرح زیر است:

        {pdf_text}

        لطفاً به سوال زیر بر اساس همین اطلاعات پاسخ بده:
        {user_msg}
        """

        response = model.generate_content(prompt)
        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
