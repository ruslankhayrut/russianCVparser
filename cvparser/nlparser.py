import json

from .helpers import TOKENIZER, ID_TOKENIZER, load_named_entities, show_json
from .education import EducationExtractor
from .workplace import WorkplaceExtractor
from .hobby import HobbyExtractor
from .socdem import SocdemExtractor

from yargy.parser import Parser
from yargy.pipelines import pipeline, caseless_pipeline


EXP_TITLE = pipeline(['Опыт работы'])
EDU_TITLE = pipeline(['Образование'])
HOBBY_TITLE = caseless_pipeline(['Хобби', 'Увлечения'])


def parse(text):

    named_entities = load_named_entities(text)
    socdem_tokens = exp_tokens = edu_tokens = hobby_tokens = tokens = list(TOKENIZER(text))

    parser = Parser(EXP_TITLE, tokenizer=ID_TOKENIZER)
    exp_title = parser.find(tokens)

    parser = Parser(EDU_TITLE, tokenizer=ID_TOKENIZER)
    edu_title = parser.find(tokens)

    parser = Parser(HOBBY_TITLE, tokenizer=ID_TOKENIZER)
    hobby_title = parser.find(tokens)

    if exp_title:
        socdem_tokens = tokens[:tokens.index(exp_title.tokens[0])]
        exp_tokens = tokens[tokens.index(exp_title.tokens[0]):]

    if edu_title:
        exp_tokens = exp_tokens[:exp_tokens.index(edu_title.tokens[0])]
        edu_tokens = tokens[tokens.index(edu_title.tokens[0]):]

    if hobby_title:
        edu_tokens = edu_tokens[:edu_tokens.index(hobby_title.tokens[0])]
        hobby_tokens = tokens[tokens.index(hobby_title.tokens[0]):]

    socdem_match = SocdemExtractor(named_entities['person_names']).find(socdem_tokens)
    exp_matches = WorkplaceExtractor(named_entities['orgnames']).find(exp_tokens)
    edu_matches = EducationExtractor().find(edu_tokens)
    hobby_matches = HobbyExtractor().find(hobby_tokens)

    socdem_fact = socdem_match.fact.as_json
    exp_facts = [match.fact.as_json for match in exp_matches]
    edu_facts = [match.fact.as_json for match in edu_matches]
    hobby_facts = [match.fact.as_json for match in hobby_matches]

    d = {
        'socdem': socdem_fact,
        'career': exp_facts,
        'education': edu_facts,
        'hobby': hobby_facts
    }

    return d


def dump_as_json(string):
    json_string = json.dumps(string, ensure_ascii=False, indent=2)
    return json_string
