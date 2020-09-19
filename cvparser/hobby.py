from yargy import (
    rule, or_, Parser
)

from yargy.predicates import (
    eq, gram
)
from yargy.pipelines import (
    caseless_pipeline, pipeline
)
from yargy.interpretation import (
    fact, attribute
)

from .helpers import ID_TOKENIZER, select_span_tokens, show_matches

Hobby = fact(
    'Hobby',
    [
        attribute('name').repeatable()
    ]
)

HYPHEN = rule(pipeline(['-', '—', '–']))
COLON = rule(eq(':'))
COMMA = rule(eq(','))
DOT = rule(eq('.'))

TITLES = caseless_pipeline(['Хобби', 'Увлечения'])

TITLE = rule(
    TITLES,
    or_(
        COLON,
        HYPHEN
    )
)

ITEM = rule(or_(
    gram('NOUN'),
    gram('ADJF')
).repeatable(max=3)).interpretation(Hobby.name)

HOBBY_ITEMS = rule(
    or_(TITLE,
        ITEM,
        COMMA,
        DOT)
)

HOBBIES = rule(
    TITLE,
    rule(ITEM,
         or_(COMMA, DOT)).repeatable(),
).interpretation(Hobby)


class HobbyExtractor:

    @staticmethod
    def find(tokens):
        parser = Parser(HOBBY_ITEMS, tokenizer=ID_TOKENIZER)
        matches = parser.findall(tokens)
        spans = [_.span for _ in matches]

        tokens = list(select_span_tokens(tokens, spans))
        # print([_.value for _ in tokens])

        parser = Parser(HOBBIES, tokenizer=ID_TOKENIZER)

        matches = list(parser.findall(tokens))
        return matches
