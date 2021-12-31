import re

import unicodedata

sc_str = r'!"#$%&\'\*+-:<=>?@[\\/[^_`{|}~()'


def clean_text(text, min_sent_len=0):
    search = re.search(r'(\w{1}:\\)(.)*\\(.)*.(\w){2,4}', text)
    if search:
        start = search.start()
        text = text[:start]

    text = re.sub(r'((,)+(-)?(\d){1,})\.(\d){1,}|((,)(-)?(\d)+)|((\n)(\d)+)', '', text)
    text = re.sub(r'\<.*?\>', '', text)

    def is_pua(c):
        return unicodedata.category(c) == 'Co'

    if not text.strip():
        return ''

    if 'javascript' in text:
        idx = text.index('javascript')
        text = text[:idx]

    # text = re.sub(r'[^a-zA-Z0-9.,\?\s]', '', text)
    text = text.replace('?', '')
    text = re.sub(r'(\n|\r|\t|\xa0){2,}', '. ', text)
    text = re.sub(r'(\n|\r|\t|\xa0)', ' ', text)
    text = text.replace(u'\n', u' ').replace(u'\r', u' ')
    text = text.replace(u'\xa0', u' ')
    text = re.sub(r'(\\xa|\\u2)([0-9a-zA-Z]+)', '', text)
    text = text.translate(str.maketrans(dict.fromkeys(sc_str)))
    text = "".join([char for char in text if not is_pua(char)]).strip()
    text = re.sub(' +', ' ', text)
    text = re.sub(r'(?<![A-Z\W])(?=[A-Z])', ' ', text)
    text = ' '.join(filter(None, re.split(r'\s|([^\w@#])', text)))
    text = '. '.join([x.strip() for x in text.split('.') if x.strip() and len(x.strip().split()) >= min_sent_len])
    text = text.replace('committed to connecting the world. you are here itu home itut', '')
    text = text.replace('committed to connecting the world. ', '')
    text = re.sub(r'\b(\w{1}|\d{1,})\b', '', text)
    text = text[:50000]

    return text
