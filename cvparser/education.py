import os

from yargy import (
    rule, or_, and_, Parser
)

from yargy.predicates import (
    gte, lte
)
from yargy.pipelines import (
    caseless_pipeline
)
from yargy.interpretation import (
    fact
)

from .helpers import load_lines, ID_TOKENIZER, select_span_tokens

Date = fact(
    'Date',
    ['month', 'year']
)

Education = fact(
        'Education',
        ['year', 'name', 'specialization']
    )

"""
Creating dicts
"""
FOLDER = os.path.dirname(__file__)
UNI_NAMES = load_lines(os.path.join(FOLDER, 'dicts/VUZY.txt'))
SPECIALIZATIONS = load_lines(os.path.join(FOLDER, 'dicts/specs_only.txt'))

UNI_NAME = caseless_pipeline(UNI_NAMES)
SPECIALIZATION = caseless_pipeline(SPECIALIZATIONS)
"""
"""

YEAR = and_(
    gte(1900),
    lte(2100)
).interpretation(
    Date.year.custom(int)
)

EDU_ELEM = rule(
    or_(
        YEAR,
        UNI_NAME,
        SPECIALIZATION
    )
)

EDUCATION = rule(
    YEAR.interpretation(Education.year),
    UNI_NAME.interpretation(Education.name),
    SPECIALIZATION.optional().interpretation(Education.specialization)
).interpretation(Education)


class EducationExtractor:

    @staticmethod
    def find(tokens):
        parser = Parser(EDU_ELEM, tokenizer=ID_TOKENIZER)
        matches = parser.findall(tokens)
        spans = [_.span for _ in matches]

        tokens = list(select_span_tokens(tokens, spans))
        # print([_.value for _ in tokens])

        parser = Parser(EDUCATION, tokenizer=ID_TOKENIZER)

        matches = list(parser.findall(tokens))
        return matches
