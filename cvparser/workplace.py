import os

from yargy import (
    rule, or_, and_, not_, Parser
)

from yargy.predicates import (
    eq,
    dictionary,
    gte, lte
)
from yargy.pipelines import (
    caseless_pipeline, pipeline
)
from yargy.interpretation import (
    fact
)


from .helpers import load_lines, load_named_entities, select_span_tokens, ID_TOKENIZER


Workplace = fact(
    'Workplace',
    ['period', 'org_name', 'occupation']
)


"""
Dicts
"""
FOLDER = os.path.dirname(__file__)
OCCUPATIONS = load_lines(os.path.join(FOLDER, 'dicts/occupations.txt'))
"""
"""

HYPHEN = rule(pipeline(['-', '—', '–']))
COMMA = eq(',')

MONTHS = {
    'январь': 1,
    'февраль': 2,
    'март': 3,
    'апрель': 4,
    'май': 5,
    'июнь': 6,
    'июль': 7,
    'август': 8,
    'сентябрь': 9,
    'октябрь': 10,
    'ноябрь': 11,
    'декабрь': 12
}


MONTH = and_(
    gte(1),
    lte(12)
)

Date = fact(
    'Date',
    ['month', 'year']
)

MONTH_NAME = dictionary(
    MONTHS
).interpretation(
    Date.month.normalized().custom(MONTHS.get)
)

YEAR = and_(
    gte(1900),
    lte(2100)
).interpretation(
    Date.year.custom(int)
)

DATE = rule(
    MONTH_NAME,
    YEAR
).interpretation(
    Date
)

Work_period = fact(
    'Work_period',
    ['from_date', 'to_date']
)

FROM_DATE = DATE.interpretation(Work_period.from_date)
TO_DATE = DATE.interpretation(Work_period.to_date)

PERIOD = rule(
    FROM_DATE, HYPHEN.optional(),
    or_(TO_DATE,
        pipeline(['н.в.', 'настоящее время', 'работает сейчас'])
        )
).interpretation(Work_period).interpretation(Workplace.period)


OCC_NAMES = caseless_pipeline(OCCUPATIONS)

OCCUPATION = rule(
    or_(rule(OCC_NAMES),
        rule(
            OCC_NAMES,
            COMMA,
            not_(eq(OCC_NAMES)).repeatable(max=3),
            OCC_NAMES))).interpretation(Workplace.occupation)


def update_rules(orgnames):

    ORGANIZATION = caseless_pipeline(orgnames).interpretation(Workplace.org_name)

    WORKPLACE_ELEM = rule(
        or_(PERIOD,
            ORGANIZATION,
            OCCUPATION
            )
    )

    WORKPLACE = rule(
        PERIOD,
        or_(rule(ORGANIZATION,
                 OCCUPATION.optional()),
            rule(ORGANIZATION.optional(),
                 OCCUPATION),
            rule(OCCUPATION,
                 ORGANIZATION.optional()),
            rule(OCCUPATION.optional(),
                 ORGANIZATION))
    ).interpretation(Workplace)

    return WORKPLACE_ELEM, WORKPLACE


class WorkplaceExtractor:
    def __init__(self, possible_orgnames=()):
        self.WORKPLACE_ELEM, self.WORKPLACE = update_rules(possible_orgnames)

    def find(self, tokens):
        parser = Parser(self.WORKPLACE_ELEM, tokenizer=ID_TOKENIZER)
        matches = parser.findall(tokens)
        spans = [_.span for _ in matches]

        tokens = list(select_span_tokens(tokens, spans))
        # print([_.value for _ in tokens])

        parser = Parser(self.WORKPLACE, tokenizer=ID_TOKENIZER)

        matches = list(parser.findall(tokens))
        return matches
