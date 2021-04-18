from datetime import datetime
import re


class UnknownLang(Exception):
    pass


DELETE_UNKNOWN_PATTERN = r'[^#№.A-Za-zА-Яа-я0-9 ]'

RU_MONTHS = [
    'Янв',
    'Фев',
    'Мар',
    'Апр',
    'Май',
    'Июн',
    'Июл',
    'Авг',
    'Сен',
    'Окт',
    'Ноя',
    'Дек',
]

MAX_TITLE_LENGTH = 80


def format_title(pattern: str, title: str, name: str, date: datetime, lang: str = 'ru') -> str:
    title = delete_unknown_symbols_and_spaces(title)
    date_str = create_date_str(date, lang)

    pattern_without_title = ''.join(pattern.split('{title}'))
    without_title = pattern_without_title.format(name=name, date=date_str)
    max_title_length = MAX_TITLE_LENGTH - len(without_title)

    title = short_title(title, max_title_length)

    formatted_title = pattern.format(title=title, name=name, date=date_str)

    return formatted_title


def delete_unknown_symbols_and_spaces(s: str) -> str:
    reg_return = re.sub(DELETE_UNKNOWN_PATTERN, '', s)
    reg_return = reg_return.strip()
    words = reg_return.split(' ')
    words = filter(lambda word: word != '' and 'http' not in word, words)
    return ' '.join(words)


def short_title(s: str, max_length) -> str:
    while True:
        if len(s) < max_length:
            break
        else:
            s = delete_last_word(s)

    return s


def delete_last_word(s: str) -> str:
    return s.rsplit(' ', 1)[0]


def create_date_str(date, lang):
    if lang == 'ru':
        date_str = '{}-{}-{}'.format(date.day, RU_MONTHS[date.month - 1], date.year)
    else:
        raise UnknownLang(lang)

    return date_str
