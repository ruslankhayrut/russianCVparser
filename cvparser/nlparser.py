from .helpers import TOKENIZER, ID_TOKENIZER, load_named_entities
from .education import EducationExtractor
from .workplace import WorkplaceExtractor
from .hobby import HobbyExtractor

from yargy.parser import Parser
from yargy.pipelines import pipeline, caseless_pipeline


EXP_TITLE = pipeline(['Опыт работы'])
EDU_TITLE = pipeline(['Образование'])
EXTRA_EDU_TITLE = caseless_pipeline(['Курсы', 'Сертификаты'])
HOBBY_TITLE = caseless_pipeline(['Хобби', 'Увлечения'])


def parse(text):

    named_entities = load_named_entities(text)
    exp_tokens = edu_tokens = hobby_tokens = tokens = list(TOKENIZER(text))
    extra_edu_tokens = []

    parser = Parser(EXP_TITLE, tokenizer=ID_TOKENIZER)
    exp_title = parser.find(tokens)

    parser = Parser(EDU_TITLE, tokenizer=ID_TOKENIZER)
    edu_title = parser.find(tokens)

    parser = Parser(HOBBY_TITLE, tokenizer=ID_TOKENIZER)
    hobby_title = parser.find(tokens)

    if exp_title:
        exp_tokens = tokens[tokens.index(exp_title.tokens[0]):]

    if edu_title:
        exp_tokens = exp_tokens[:exp_tokens.index(edu_title.tokens[0])]
        edu_tokens = tokens[tokens.index(edu_title.tokens[0]):]

    if hobby_title:
        edu_tokens = edu_tokens[:edu_tokens.index(hobby_title.tokens[0])]
        hobby_tokens = tokens[tokens.index(hobby_title.tokens[0]):]

    if len(edu_tokens) < len(tokens):
        parser = Parser(EXTRA_EDU_TITLE, tokenizer=ID_TOKENIZER)
        extra_edu_title = parser.find(edu_tokens)
        if extra_edu_title:
            pivot_index = edu_tokens.index(extra_edu_title.tokens[0])
            edu_tokens, extra_edu_tokens = edu_tokens[:pivot_index], edu_tokens[pivot_index:]

    exp_matches = WorkplaceExtractor(named_entities).find(exp_tokens)
    edu_matches = EducationExtractor().find(edu_tokens)
    extra_edu_matches = EducationExtractor(extra=True).find(extra_edu_tokens)
    hobby_matches = HobbyExtractor().find(hobby_tokens)

    exp_facts = [match.fact.as_json for match in exp_matches]
    edu_facts = [match.fact.as_json for match in edu_matches]
    extra_edu_facts = [match.fact.as_json for match in extra_edu_matches]
    hobby_facts = [match.fact.as_json for match in hobby_matches]

    d = {
        'experience': exp_facts,
        'education': edu_facts,
        'extra_education': extra_edu_facts,
        'hobby': hobby_facts
    }

    return d


class CVparser:

    @staticmethod
    def parse_text(text):
        return parse(text)
