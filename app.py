from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve
import google.generativeai as genai
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF

load_dotenv()

app = Flask(__name__)
CORS(app)

# پیکربندی کلید Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# مدل مورد استفاده (می‌توان Flash یا Pro انتخاب کرد)
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_pdf(pdf_file):
    """استخراج متن از فایل PDF"""
    text = ""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    for page in doc:
        text += page.get_text()
    return text.strip()

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        user_msg = request.form.get("message", "")
        if not user_msg:
            return jsonify({"error": "No message provided"}), 400

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if not file.filename.endswith(".pdf"):
            return jsonify({"error": "Invalid file type. Please upload a PDF file."}), 400

        pdf_text = extract_text_from_pdf(file)
        if not pdf_text:
            return jsonify({"error": "Failed to extract text from PDF."}), 500

        # ساخت پرامپت برای AI
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
