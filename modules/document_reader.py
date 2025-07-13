import fitz

def read_pdf(path):
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)

def read_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
