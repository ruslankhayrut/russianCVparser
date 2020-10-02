# General information

Parser extracts as many as possible information from the CV text. It uses `natasha` library for 
entities recognition and `yargy` parser for rule-based parsing.

Information that can be extracted:

* socdem:
  - name,
  - gender,
  - date_of_birth,
  - age,
  - location
* career:
  - period,
  - org_name,
  - occupation
* education:
  - year,
  - name,
  - specialization
* hobby:
  - name
# Installation
`pip install russianCVparser`

# Usage
Parser supports documents in **docx, pdf and txt** formats. 
```
from russianCVparser import CVparser, Document, show_json

parser = CVparser()
document = Document('path/to/doc.pdf')
data = parser.parse_text(document.text) # returns an OrderedDict instance
show_json(data)
```
# Example
```
from russianCVparser import CVparser, Document, show_json

parser = CVparser()
document = Document('CV.pdf')
data = parser.parse_text(document.text)
show_json(data)
```
Output:
```
{
  "socdem": {
    "name": "Иванов Иван Иванович",
    "gender": "male",
    "date_of_birth": {
      "year": 1981,
      "month": 5,
      "day": 2
    },
    "age": "39 лет",
    "location": {
      "name": "Казань"
    }
  },
  "career": [
    {
      "period": {
        "from_date": {
          "month": 12,
          "year": 2017
        }
      },
      "org_name": "ООО "Инвест-консалт"",
      "occupation": "Ведущий специалист"
    },
    {
      "period": {
        "from_date": {
          "month": 2,
          "year": 2011
        },
        "to_date": {
          "month": 6,
          "year": 2017
        }
      },
      "org_name": "Казгорсеть",
      "occupation": "Ведущий специалист"
    },
    {
      "period": {
        "from_date": {
          "month": 2,
          "year": 2010
        },
        "to_date": {
          "month": 2,
          "year": 2011
        }
      },
      "org_name": "ООО Адванс",
      "occupation": "Аналитик"
    }
  ],
  "education": [
    {
      "year": 2015,
      "name": "Российский государственный аграрный университет"
    },
    {
      "year": 2016,
      "name": "Московский Государственный Технический Университет"
    }
  ],
  "hobby": [
    {
      "name": [
        "футбол",
        "рыбалка",
        "шахматы"
      ]
    }
  ]
}
```