from cvparser import Document, CVParser
from pprint import pprint

parser = CVParser()
d = Document('CVex.docx')

pprint(parser.parse_text(d.text))