import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO

def extract_articles_from_docx(docx_bytes):
    with zipfile.ZipFile(BytesIO(docx_bytes)) as docx_zip:
        with docx_zip.open('word/document.xml') as doc_xml_file:
            tree = ET.parse(doc_xml_file)
            root = tree.getroot()

    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    articles = []
    buffer = ""

    for para in root.findall('.//w:body/w:p', ns):
        text = ''.join(node.text or '' for node in para.findall('.//w:t', ns))
        buffer += text.strip() + '\n'

        if para.find('.//w:pPr/w:pBdr', ns) is not None:
            articles.append(buffer.strip())
            buffer = ""

    if buffer.strip():
        articles.append(buffer.strip())

    return articles
