import random
import string
from datetime import datetime, date


def random_datetime():
    year = random.randint(1970, 2017)
    month = random.randint(1, 12)
    day = random.randint(1, 28)

    return datetime(year, month, day)


def generate_row(entity_description):
    properties = entity_description['column_map']

    row = {}

    for prop in properties:
        prop_type = properties[prop]['type']

        if prop_type == 'string':
            value = ''.join(random.choice(string.ascii_letters) for _ in range(26))
        elif prop_type == 'int':
            value = random.randint(0, 999999)
        elif prop_type == 'float':
            value = random.random()*7
        elif prop_type == 'boolean':
            value = random.random() > 0.5
        elif prop_type == 'date':
            value = random_datetime().date().isoformat()
        elif prop_type == 'timestamp':
            value = random_datetime().isoformat()
        else:
            value = None

        row[prop] = value

    return row
