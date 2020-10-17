import os
import sys
import re
from io import StringIO
import docx2txt
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


class Document:
    def __init__(self, path: str):
        self.__path = path

    @property
    def text(self):
        if not os.path.exists(self.__path):
            sys.stdout.write('File not found')
            raise FileNotFoundError

        text = ''
        ext = self.__extension(self.__path)

        with open(self.__path, 'rb') as file:
            if ext not in ('txt', 'docx', 'pdf'):
                sys.stdout.write(f'Incorrect file extension. Expected .txt, .docx or .pdf, {ext} found.')
                raise TypeError

            if ext == 'txt':
                text = file.read().decode('utf-8')
            elif ext == 'docx':
                text = docx2txt.process(self.__path)
            elif ext == 'pdf':
                text = self.__extract_from_pdf(file)

        return text

    @staticmethod
    def __extension(filename):
        if '.' not in filename:
            return
        ext = filename.rsplit('.', 1)[1].lower()
        return ext

    @staticmethod
    def __extract_from_pdf(file):
        parser = PDFParser(file)
        doc = PDFDocument(parser)
        resource_manager = PDFResourceManager()
        output_string = StringIO()
        converter = TextConverter(resource_manager, output_string, laparams=LAParams(char_margin=15,
                                                                                     line_margin=0.5,
                                                                                     boxes_flow=0))

        page_interpreter = PDFPageInterpreter(resource_manager, converter)

        for page in PDFPage.create_pages(doc):
            page_interpreter.process_page(page)

        text = output_string.getvalue()
        text = re.sub(r'(Резюме обновлено)([А-Яа-я\d :])+', '', text)
        converter.close()
        output_string.close()
        return text
