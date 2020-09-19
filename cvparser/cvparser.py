from .nlparser import parse
import json

class CVParser:
    def __init__(self):
        self.career_facts = []
        self.edu_facts = []
        self.hobby_facts = []

    def parse_text(self, text):
        res = parse(text)
        return res
