import pdfplumber

def extract_texts_from_pdfs(files):
    resume_texts = {}
    for uploaded_file in files:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                text = "\n".join(page.extract_text() or '' for page in pdf.pages)
            resume_texts[uploaded_file.name] = text.strip()
        except Exception as e:
            resume_texts[uploaded_file.name] = f"[Error reading file: {str(e)}]"
    return resume_texts
