from flask import Flask, request, jsonify
import os
import re
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from fuzzywuzzy import fuzz, process
from pyzbar.pyzbar import decode
from PIL import Image
import shutil

app = Flask(__name__)

# === Config ===
THRESHOLD_BANK = 8
THRESHOLD_SALARY = 7
OCR_TMP_PATH = "tmp_ocr_images"

# === Keyword Lists ===
bank_keywords = [
    "Statement of Account", "Account Number", "Account No.", "Account #",
    "Debit", "Credit", "Deposit", "Withdrawal",
    "Account Title", "Account Name", "Customer Name", "Cust. Name",
    "Description", "Transaction Detail", "Voucher Narration", "IBAN"
]

salary_keywords = [
    "Wages", "Pay Slip", "Salary Slip", "Earning", "Deduction",
    "Account Number", "Account No.", "Account #",
    "Net Amount", "Basic Salary", "Allowances", "Payment Date", "IBAN"
]


def detect_qr_in_pdf(pdf_path):
    pages = convert_from_path(pdf_path)
    for page in pages:
        img = page.convert("RGB")
        decoded_objects = decode(img)
        if decoded_objects:
            return True
    return False


def is_scanned_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        if page.extract_text().strip():
            return False
    return True


def extract_text_with_ocr(pdf_path):
    os.makedirs(OCR_TMP_PATH, exist_ok=True)
    pages = convert_from_path(pdf_path)
    full_text = ""
    for i, page in enumerate(pages):
        image_path = os.path.join(OCR_TMP_PATH, f"page_{i}.png")
        page.save(image_path, "PNG")
        text = pytesseract.image_to_string(image_path)
        full_text += text + " "
    shutil.rmtree(OCR_TMP_PATH)
    return full_text


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    return " ".join([page.extract_text() for page in reader.pages])


def keyword_match_count(text, keyword_list, check_qr=False, pdf_path=None):
    matched = 0
    lowered_text = text.lower()
    lines = lowered_text.splitlines()
    text_words = set(lowered_text.split())

    for keyword in keyword_list:
        keyword_lower = keyword.lower()
        keyword_words = set(keyword_lower.split())
        best_score = 0

        for line in lines:
            score = fuzz.token_set_ratio(keyword_lower, line)
            best_score = max(best_score, score)

        if (
            best_score >= 80
            or keyword_lower in lowered_text
            or keyword_words.issubset(text_words)
        ):
            matched += 1
        
        if keyword.lower() == 'salary slip' or keyword.lower() == 'bank statement':
            matched += 3

    if check_qr and pdf_path and detect_qr_in_pdf(pdf_path):
        matched += 1

    return matched


def is_pdf_modified(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        metadata = reader.metadata

        creation_date = metadata.get("/CreationDate")
        mod_date = metadata.get("/ModDate")

        if creation_date and mod_date and creation_date != mod_date:
            return True, creation_date, mod_date
        else:
            return False, creation_date, mod_date
    except Exception as e:
        return False, None, f"Metadata error: {e}"


def get_text_from_pdf(pdf_path):
    scanned = is_scanned_pdf(pdf_path)
    text = extract_text_with_ocr(pdf_path) if scanned else extract_text_from_pdf(pdf_path)
    return text, scanned


@app.route('/classify/bank-statement', methods=['POST'])
def classify_bank_statement():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    pdf_path = "temp_input.pdf"
    file.save(pdf_path)

    try:
        text, scanned = get_text_from_pdf(pdf_path)
        match_count = keyword_match_count(text, bank_keywords, check_qr=True, pdf_path=pdf_path)
        classification = "Bank Statement" if match_count >= THRESHOLD_BANK else "Other"

        was_modified, created, modified = is_pdf_modified(pdf_path)

        return jsonify({
            "classification": classification,
            "match_count": match_count,
            "scanned": scanned,
            "pdf_modified": was_modified,
            "creation_date": created,
            "modification_date": modified
        })
    finally:
        os.remove(pdf_path)


@app.route('/classify/salary-slip', methods=['POST'])
def classify_salary_slip():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    pdf_path = "temp_input.pdf"
    file.save(pdf_path)

    try:
        text, scanned = get_text_from_pdf(pdf_path)
        match_count = keyword_match_count(text, salary_keywords, check_qr=False)
        classification = "Salary Slip" if match_count >= THRESHOLD_SALARY else "Other"

        was_modified, created, modified = is_pdf_modified(pdf_path)

        return jsonify({
            "classification": classification,
            "match_count": match_count,
            "scanned": scanned,
            "pdf_modified": was_modified,
            "creation_date": created,
            "modification_date": modified
        })
    finally:
        os.remove(pdf_path)


if __name__ == '__main__':
    app.run(debug=True)
