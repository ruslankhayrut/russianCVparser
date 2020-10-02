import os
import sys
from io import StringIO
import docx2txt
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams


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
        resource_manager = PDFResourceManager()
        fake_file_handle = StringIO()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams(line_margin=0.1,
                                                                                        char_margin=20,
                                                                                        boxes_flow=0.4))
        page_interpreter = PDFPageInterpreter(resource_manager, converter)

        for page in PDFPage.get_pages(file,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()
        converter.close()
        fake_file_handle.close()
        return text
