import os

from yargy import (
    rule, or_, and_, Parser, not_
)

from yargy.predicates import (
    gte, lte, eq
)
from yargy.pipelines import (
    caseless_pipeline, morph_pipeline
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

UNI_NAMES_GEN = load_lines(os.path.join(FOLDER, 'dicts/VUZY.txt'))
UNI_NAMES = set(UNI_NAMES_GEN)

SPECIALIZATIONS = load_lines(os.path.join(FOLDER, 'dicts/specs_only.txt'))

SPECIALIZATION = caseless_pipeline(SPECIALIZATIONS).interpretation(Education.specialization)
"""
"""

YEAR = and_(
    gte(1900),
    lte(2100)
).interpretation(
    Date.year.custom(int)
).interpretation(Education.year)

UNI_NAME_RULE = rule(
    or_(
        rule(
            or_(eq('Филиал'), eq('филиал')),
            morph_pipeline(UNI_NAMES)
        ),
        caseless_pipeline(UNI_NAMES)
    )
).interpretation(Education.name)

ANON_COURSE_NAME = rule(
    and_(
        not_(eq('имени')),
        not_(eq('.')),
    ).repeatable(max=5)
).interpretation(Education.name)


EDU_ELEM = rule(
    or_(
        YEAR,
        UNI_NAME_RULE,
        SPECIALIZATION
    )
)

EDUCATION = rule(
    YEAR,
    UNI_NAME_RULE,
    SPECIALIZATION.optional()
).interpretation(Education)

EXTRA_EDU_ELEM = rule(
    or_(
        YEAR,
        or_(
            UNI_NAME_RULE,
            ANON_COURSE_NAME),
        SPECIALIZATION
    )
)

EXTRA_EDUCATION = rule(
    YEAR,
    or_(
        UNI_NAME_RULE,
        ANON_COURSE_NAME
    ),
    SPECIALIZATION.optional()
).interpretation(Education)

# t = open('CV.txt', 'r', encoding='utf-8').read()
#
# show_matches(ANON_COURSE_NAME, "Московский Государственный Технический Университет имени Н. Э. Баумана")
# exit()

class EducationExtractor:

    def __init__(self, extra=False):
        self.ELEM = EDU_ELEM if not extra else EXTRA_EDU_ELEM
        self.EDU = EDUCATION if not extra else EXTRA_EDUCATION

    def find(self, tokens):
        parser = Parser(self.ELEM, tokenizer=ID_TOKENIZER)
        matches = parser.findall(tokens)
        spans = [_.span for _ in matches]

        tokens = list(select_span_tokens(tokens, spans))
        # print([_.value for _ in tokens])

        parser = Parser(self.EDU, tokenizer=ID_TOKENIZER)

        matches = list(parser.findall(tokens))
        return matches
