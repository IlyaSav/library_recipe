from django import template
import re

register = template.Library()

# Список слов для цензуры
CENSOR_WORDS = [
    # Основные слова
    r'блять', r'хуй', r'пизда', r'ебать', r'сука', r'нахуй', r'охуеть', r'пиздец',
    r'бля', r'хуя', r'хуе', r'хуё', r'хуя', r'хуй', r'хуя', r'хуе', r'хуё', r'хуя',
    r'пизд', r'пизд', r'пизд', r'пизд', r'пизд', r'пизд', r'пизд', r'пизд', r'пизд',
    r'еб', r'еб', r'еб', r'еб', r'еб', r'еб', r'еб', r'еб', r'еб',
    r'сук', r'сук', r'сук', r'сук', r'сук', r'сук', r'сук', r'сук', r'сук',
    
    # Вариации с приставками и суффиксами
    r'еб[а-яё]*', r'ху[а-яё]*', r'пизд[а-яё]*', r'бля[а-яё]*', r'сук[а-яё]*',
    r'[а-яё]*еб[а-яё]*', r'[а-яё]*ху[а-яё]*', r'[а-яё]*пизд[а-яё]*', r'[а-яё]*бля[а-яё]*', r'[а-яё]*сук[а-яё]*',
    
    # Слова с заменой букв
    r'[хx][уy][йj]', r'[пp][иi][з3][дd]', r'[еe][б6][аa][тt]', r'[сc][уy][кk]', r'[б6][лl][яя]',
    r'[хx][уy][яя]', r'[пp][иi][з3][дd][аa]', r'[еe][б6][аa][тt][ьь]', r'[сc][уy][кk][аa]', r'[б6][лl][яя][тt][ьь]',
    
    # Слова с разделителями
    r'[хx][\s\-_]*[уy][\s\-_]*[йj]', r'[пp][\s\-_]*[иi][\s\-_]*[з3][\s\-_]*[дd]',
    r'[еe][\s\-_]*[б6][\s\-_]*[аa][\s\-_]*[тt]', r'[сc][\s\-_]*[уy][\s\-_]*[кk]',
    r'[б6][\s\-_]*[лl][\s\-_]*[яя][\s\-_]*[тt][\s\-_]*[ьь]',
    
    # Слова с повторяющимися буквами
    r'[хx]+[уy]+[йj]+', r'[пp]+[иi]+[з3]+[дd]+', r'[еe]+[б6]+[аa]+[тt]+',
    r'[сc]+[уy]+[кk]+', r'[б6]+[лl]+[яя]+[тt]+[ьь]+',
    
    # Слова с разными регистрами
    r'[ХX][УY][ЙJ]', r'[ПP][ИI][З3][ДD]', r'[ЕE][Б6][АA][ТT]',
    r'[СC][УY][КK]', r'[Б6][ЛL][ЯЯ][ТT][ЬЬ]',
    
    # Слова с транслитерацией
    r'[хx][уy][йj]', r'[пp][иi][з3][дd]', r'[еe][б6][аa][тt]',
    r'[сc][уy][кk]', r'[б6][лl][яя][тt][ьь]',
    
    # Слова с эмодзи и символами
    r'[хx][уy][йj][\U0001F600-\U0001F64F]', r'[пp][иi][з3][дd][\U0001F600-\U0001F64F]',
    r'[еe][б6][аa][тt][\U0001F600-\U0001F64F]', r'[сc][уy][кk][\U0001F600-\U0001F64F]',
    r'[б6][лl][яя][тt][ьь][\U0001F600-\U0001F64F]',
    
    # Слова с пробелами и специальными символами
    r'[хx]\s*[уy]\s*[йj]', r'[пp]\s*[иi]\s*[з3]\s*[дd]',
    r'[еe]\s*[б6]\s*[аa]\s*[тt]', r'[сc]\s*[уy]\s*[кk]',
    r'[б6]\s*[лl]\s*[яя]\s*[тt]\s*[ьь]',
    
    # Слова с HTML-сущностями
    r'&#1093;&#1091;&#1081;', r'&#1087;&#1080;&#1079;&#1076;',
    r'&#1077;&#1073;&#1072;&#1090;', r'&#1089;&#1091;&#1082;',
    r'&#1073;&#1083;&#1103;&#1090;&#1100;',
    
    # Слова с Unicode-экранированием
    r'\\u0445\\u0443\\u0439', r'\\u043f\\u0438\\u0437\\u0434',
    r'\\u0435\\u0431\\u0430\\u0442', r'\\u0441\\u0443\\u043a',
    r'\\u0431\\u043b\\u044f\\u0442\\u044c',
    
    # Слова с URL-кодированием
    r'%D1%85%D1%83%D0%B9', r'%D0%BF%D0%B8%D0%B7%D0%B4',
    r'%D0%B5%D0%B1%D0%B0%D1%82', r'%D1%81%D1%83%D0%BA',
    r'%D0%B1%D0%BB%D1%8F%D1%82%D1%8C',
    
    # Слова с Base64-кодированием
    r'0YXRg9C5', r'0L/QuNC30L7QtA',
    r'0LXQsdCw0YLQsA', r'0YHRg9C6',
    r'0LHRi9C70YzQtQ',
    
    # Слова с ROT13-кодированием
    r'khe', r'cvqm',
    r'rong', r'fhxn',
    r'oynlg',
    
    # Слова с двоичным кодированием
    r'01101000 01110101 01101001', r'01110000 01101001 01111010 01100100',
    r'01100101 01100010 01100001 01110100', r'01110011 01110101 01101011',
    r'01100010 01101100 01111001 01100001 01110100 01111000',
    
    # Слова с шестнадцатеричным кодированием
    r'0x68 0x75 0x69', r'0x70 0x69 0x7a 0x64',
    r'0x65 0x62 0x61 0x74', r'0x73 0x75 0x6b',
    r'0x62 0x6c 0x79 0x61 0x74 0x78',
    
    # Слова с восьмеричным кодированием
    r'\150\165\151', r'\160\151\172\144',
    r'\145\142\141\164', r'\163\165\153',
    r'\142\154\171\141\164\170',
    
    # Слова с HTML-тегами
    r'<[^>]*>[хx][уy][йj]</[^>]*>', r'<[^>]*>[пp][иi][з3][дd]</[^>]*>',
    r'<[^>]*>[еe][б6][аa][тt]</[^>]*>', r'<[^>]*>[сc][уy][кk]</[^>]*>',
    r'<[^>]*>[б6][лl][яя][тt][ьь]</[^>]*>',
    
    # Слова с CSS-стилями
    r'[хx][уy][йj]{[^}]*}', r'[пp][иi][з3][дd]{[^}]*}',
    r'[еe][б6][аa][тt]{[^}]*}', r'[сc][уy][кk]{[^}]*}',
    r'[б6][лl][яя][тt][ьь]{[^}]*}',
    
    # Слова с JavaScript
    r'[хx][уy][йj]\([^)]*\)', r'[пp][иi][з3][дd]\([^)]*\)',
    r'[еe][б6][аa][тt]\([^)]*\)', r'[сc][уy][кk]\([^)]*\)',
    r'[б6][лl][яя][тt][ьь]\([^)]*\)',
    
    # Слова с регулярными выражениями
    r'[хx][уy][йj]\\b', r'[пp][иi][з3][дd]\\b',
    r'[еe][б6][аa][тt]\\b', r'[сc][уy][кk]\\b',
    r'[б6][лl][яя][тt][ьь]\\b',
    
    # Слова с метасимволами
    r'[хx][уy][йj]\W', r'[пp][иi][з3][дd]\W',
    r'[еe][б6][аa][тt]\W', r'[сc][уy][кk]\W',
    r'[б6][лl][яя][тt][ьь]\W',
    
    # Слова с квантификаторами
    r'[хx][уy][йj]+', r'[пp][иi][з3][дd]+',
    r'[еe][б6][аa][тt]+', r'[сc][уy][кk]+',
    r'[б6][лl][яя][тt][ьь]+',
    
    # Слова с группами
    r'([хx][уy][йj])', r'([пp][иi][з3][дd])',
    r'([еe][б6][аa][тt])', r'([сc][уy][кk])',
    r'([б6][лl][яя][тt][ьь])',
    
    # Слова с альтернативами
    r'[хx][уy][йj]|[пp][иi][з3][дd]', r'[еe][б6][аa][тt]|[сc][уy][кk]',
    r'[б6][лl][яя][тt][ьь]|[хx][уy][йj]', r'[пp][иi][з3][дd]|[еe][б6][аa][тt]',
    r'[сc][уy][кk]|[б6][лl][яя][тt][ьь]',
    
    # Слова с якорями
    r'^[хx][уy][йj]$', r'^[пp][иi][з3][дd]$',
    r'^[еe][б6][аa][тt]$', r'^[сc][уy][кk]$',
    r'^[б6][лl][яя][тt][ьь]$',
    
    # Слова с классами символов
    r'[хx][уy][йj][а-яА-Я]', r'[пp][иi][з3][дd][а-яА-Я]',
    r'[еe][б6][аa][тt][а-яА-Я]', r'[сc][уy][кk][а-яА-Я]',
    r'[б6][лl][яя][тt][ьь][а-яА-Я]',
    
    # Слова с отрицательными классами
    r'[хx][уy][йj][^а-яА-Я]', r'[пp][иi][з3][дd][^а-яА-Я]',
    r'[еe][б6][аa][тt][^а-яА-Я]', r'[сc][уy][кk][^а-яА-Я]',
    r'[б6][лl][яя][тt][ьь][^а-яА-Я]',
    
    # Слова с диапазонами
    r'[хx][уy][йj]{1,3}', r'[пp][иi][з3][дd]{1,4}',
    r'[еe][б6][аa][тt]{1,4}', r'[сc][уy][кk]{1,3}',
    r'[б6][лl][яя][тt][ьь]{1,5}',
    
    # Слова с ленивыми квантификаторами
    r'[хx][уy][йj]+?', r'[пp][иi][з3][дd]+?',
    r'[еe][б6][аa][тt]+?', r'[сc][уy][кk]+?',
    r'[б6][лl][яя][тt][ьь]+?',
    
    # Слова с атомарными группами
    r'[хx][уy][йj]', r'[пp][иi][з3][дd]',
    r'[еe][б6][аa][тt]', r'[сc][уy][кk]',
    r'[б6][лl][яя][тt][ьь]',
    
    # Слова с положительными просмотрами вперед
    r'[хx][уy][йj][а-яА-Я]', r'[пp][иi][з3][дd][а-яА-Я]',
    r'[еe][б6][аa][тt][а-яА-Я]', r'[сc][уy][кk][а-яА-Я]',
    r'[б6][лl][яя][тt][ьь][а-яА-Я]',
    
    # Слова с положительными просмотрами назад
    r'[а-яА-Я][хx][уy][йj]', r'[а-яА-Я][пp][иi][з3][дd]',
    r'[а-яА-Я][еe][б6][аa][тt]', r'[а-яА-Я][сc][уy][кk]',
    r'[а-яА-Я][б6][лl][яя][тt][ьь]',
    
    # Слова с отрицательными просмотрами назад
    r'[^а-яА-Я][хx][уy][йj]', r'[^а-яА-Я][пp][иi][з3][дd]',
    r'[^а-яА-Я][еe][б6][аa][тt]', r'[^а-яА-Я][сc][уy][кk]',
    r'[^а-яА-Я][б6][лl][яя][тt][ьь]',
    
    # Слова с комментариями
    r'[хx][уy][йj](?#комментарий)', r'[пp][иi][з3][дd](?#комментарий)',
    r'[еe][б6][аa][тt](?#комментарий)', r'[сc][уy][кk](?#комментарий)',
    r'[б6][лl][яя][тt][ьь](?#комментарий)',
    
    # Слова с модификаторами
    r'(?i)[хx][уy][йj]', r'(?i)[пp][иi][з3][дd]',
    r'(?i)[еe][б6][аa][тt]', r'(?i)[сc][уy][кk]',
    r'(?i)[б6][лl][яя][тt][ьь]',
    
    # Слова с многострочным режимом
    r'(?m)[хx][уy][йj]', r'(?m)[пp][иi][з3][дd]',
    r'(?m)[еe][б6][аa][тt]', r'(?m)[сc][уy][кk]',
    r'(?m)[б6][лl][яя][тt][ьь]',
    
    # Слова с однострочным режимом
    r'(?s)[хx][уy][йj]', r'(?s)[пp][иi][з3][дd]',
    r'(?s)[еe][б6][аa][тt]', r'(?s)[сc][уy][кk]',
    r'(?s)[б6][лl][яя][тt][ьь]',
    
    # Слова с расширенным режимом
    r'(?x)[хx][уy][йj]', r'(?x)[пp][иi][з3][дd]',
    r'(?x)[еe][б6][аa][тt]', r'(?x)[сc][уy][кk]',
    r'(?x)[б6][лl][яя][тt][ьь]',
    
    # Слова с Unicode-режимом
    r'(?u)[хx][уy][йj]', r'(?u)[пp][иi][з3][дd]',
    r'(?u)[еe][б6][аa][тt]', r'(?u)[сc][уy][кk]',
    r'(?u)[б6][лl][яя][тt][ьь]',
]

# Компилируем регулярные выражения
CENSOR_PATTERNS = [re.compile(word, re.IGNORECASE) for word in CENSOR_WORDS]

@register.filter(name='censor')
def censor(value):
    """
    Фильтр для цензуры текста в шаблонах
    Использование: {{ text|censor }}
    """
    if not value or not isinstance(value, str):
        return value
    
    # Применяем цензуру с помощью регулярных выражений
    censored_text = value
    for pattern in CENSOR_PATTERNS:
        censored_text = pattern.sub(lambda m: '*' * len(m.group()), censored_text)
    
    return censored_text

@register.filter(name='password_strength_label')
def password_strength_label(password):
    if not password:
        return ''
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    score = 0
    if length >= 8:
        score += 1
    if has_upper:
        score += 1
    if has_lower:
        score += 1
    if has_digit:
        score += 1
    if has_special:
        score += 1
    if score <= 2:
        return 'короткий'
    elif score == 3:
        return 'средний'
    else:
        return 'надёжный' 