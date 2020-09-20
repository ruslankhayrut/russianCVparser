from yargy import (
    rule, or_, Parser
)

from yargy.predicates import (
    type,
    normalized,
)

from yargy.interpretation import (
    fact
)

from natasha.grammars import date, name, addr

from .helpers import select_span_tokens, ID_TOKENIZER


INT = type('INT')

Socdem = fact(
    'Socdem',
    ['name', 'date_of_birth', 'age', 'location']
)


AGE = rule(
    INT,
    normalized('год')
)

SOCDEM_ELEMS = rule(
    or_(
        name.NAME,
        date.DATE,
        AGE,
        addr.ADDR_PART
    )
)

SOCDEM = rule(
    name.NAME.interpretation(Socdem.name),
    date.DATE.interpretation(Socdem.date_of_birth),
    AGE.interpretation(Socdem.age),
    addr.ADDR_PART.optional().interpretation(Socdem.location)
).interpretation(Socdem)


class SocdemExtractor:

    @staticmethod
    def find(tokens):
        parser = Parser(SOCDEM_ELEMS, tokenizer=ID_TOKENIZER)
        matches = parser.findall(tokens)
        spans = [_.span for _ in matches]

        tokens = list(select_span_tokens(tokens, spans))
        # print([_.value for _ in tokens])

        parser = Parser(SOCDEM, tokenizer=ID_TOKENIZER)

        match = parser.find(tokens)
        return match

