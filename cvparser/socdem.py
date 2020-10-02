from yargy import (
    rule, or_, Parser,
)
from yargy.pipelines import pipeline

from yargy.predicates import (
    type, in_,
    normalized,
)

from yargy.interpretation import (
    fact
)

from natasha.grammars import date, addr

from .helpers import select_span_tokens, ID_TOKENIZER, show_matches, TOKENIZER, load_named_entities

INT = type('INT')

Socdem = fact(
    'Socdem',
    ['name', 'gender', 'date_of_birth', 'age', 'location']
)




GENDERS_DICT = {
    'Женщина': 'female',
    'женщина': 'female',
    'мужчина': 'male',
    'Мужчина': 'male'
}

GENDER = rule(in_(GENDERS_DICT)).interpretation(Socdem.gender.custom(GENDERS_DICT.get))

AGE = rule(
    INT,
    normalized('год')
).interpretation(Socdem.age)

LOCATION = rule(
    or_(
        addr.GOROD,
        addr.DEREVNYA,
        addr.SELO,
        addr.POSELOK
    )
).interpretation(Socdem.location)


def update_rules(name):
    NAME = pipeline(name).interpretation(Socdem.name)

    SOCDEM_ELEMS = rule(
        or_(
            NAME,
            GENDER,
            date.DATE,
            AGE,
            LOCATION
        )
    )

    SOCDEM = rule(
        NAME,
        GENDER.optional(),
        or_(
            rule(
                AGE.optional(),
                date.DATE.interpretation(Socdem.date_of_birth).optional()),
            rule(
                date.DATE.interpretation(Socdem.date_of_birth).optional(),
                AGE.optional()),
        ),
        LOCATION.optional()
    ).interpretation(Socdem)

    return SOCDEM_ELEMS, SOCDEM

# text = open('CV.txt', encoding='utf-8').read()


class SocdemExtractor:
    def __init__(self, name=()):
        self.SOCDEM_ELEMS, self.SOCDEM = update_rules(name)

    def find(self, tokens):
        parser = Parser(self.SOCDEM_ELEMS, tokenizer=ID_TOKENIZER)
        matches = parser.findall(tokens)
        spans = [_.span for _ in matches]

        tokens = list(select_span_tokens(tokens, spans))
        # print([_.value for _ in tokens])

        parser = Parser(self.SOCDEM, tokenizer=ID_TOKENIZER)

        match = parser.find(tokens)
        return match


# tokens = list(TOKENIZER(text))
#
# match = SocdemExtractor().find(tokens)
# print(match.fact.as_json)
