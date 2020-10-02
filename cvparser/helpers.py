import json
from yargy import Parser
from yargy.tokenizer import Tokenizer, MorphTokenizer, EOL
from ipymarkup import show_span_ascii_markup as show_markup
from natasha import Doc, Segmenter, NewsNERTagger, NewsEmbedding


def show_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def show_matches(rule, *lines):
    parser = Parser(rule)
    for line in lines:
        matches = parser.findall(line)
        spans = [_.span for _ in matches]

        show_markup(line, spans)


def load_lines(path):
    with open(path, encoding='utf-8') as file:
        for line in file:
            yield line.rstrip('\n')


def is_inside_span(token, span):
    token_span = token.span
    return span.start <= token_span.start and token_span.stop <= span.stop


def select_span_tokens(tokens, spans):
    for token in tokens:
        if any(is_inside_span(token, _) for _ in spans):
            yield token


def load_named_entities(text):
    doc = Doc(text)
    doc.segment(Segmenter())

    ner_tagger = NewsNERTagger(NewsEmbedding())
    doc.tag_ner(ner_tagger)

    person_names = set()
    orgnames = set()
    locations = set()
    for span in doc.spans:
        text = span.text
        if span.type == 'PER':
            person_names.add(text)
        elif span.type == 'ORG':
            orgnames.add(text)
        elif span.type == 'LOC':
            locations.add(text)

    d = {
        'person_names': person_names,
        'orgnames': orgnames,
        'locations': locations
    }

    return d


class IdTokenizer(Tokenizer):
    def __init__(self, tokenizer):
        super().__init__()
        self.tokenizer = tokenizer

    def split(self, text):
        return self.tokenizer.split(text)

    def check_type(self, type):
        return self.tokenizer.check_type(type)

    @property
    def morph(self):
        return self.tokenizer.morph

    def __call__(self, tokens):
        return tokens


TOKENIZER = MorphTokenizer().remove_types(EOL)
ID_TOKENIZER = IdTokenizer(TOKENIZER)