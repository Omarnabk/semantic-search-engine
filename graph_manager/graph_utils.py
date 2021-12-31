import json
import os
import pathlib
import uuid
from urllib.parse import urlparse

excluded_domains = ['itu.int/itudoc/', 'handle.itu.int', 'itu.int/oth', 'newslog.itu.int', 'web.archive.org',
                    '/newsarchive/', '/wftp3/', 'staging.itu.int', "/md/", '/wtpf']

excluded_extensions = ['.jpg', '.txt', '.ppsx', '.wmv', '.pptx', '.ppt', '.avi', '.7z', '.pdf', '.rar', '.jsf', '.tar',
                       'rss.aspx', '.gif', '.png', '.xlsx', '.ram', '.swf', '.mp3', '.exe', '.yuv', '.bit', '.dot',
                       '.xls', '.ics', '.epub', '.ww2', '.flv', '.wav', '.bits', '_page.print', '.form', '.xps', '.dmg',
                       '.zip', '.mobi', '.mp4', '.doc', '.mov', 'rss.asp', '.docx', '.gz', '.pps', '.xml', 'rss.xml']
excluded_extensions = list(set(excluded_extensions))


def load_json(json_path):
    with open(json_path, encoding='utf-8') as json_file:
        return json.load(json_file)


def hash_url(u):
    return uuid.uuid5(uuid.NAMESPACE_URL, u).hex


def is_valid_url_structure(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def is_valid_url(url):
    if url.lower().count('.itu.int') != 1:
        return False

    if [ex for ex in excluded_domains if ex in url]:
        return False

    suffix = pathlib.Path(url).suffix
    if suffix.lower() in excluded_extensions:
        return False

    if [x for x in excluded_extensions if url.endswith(x)]:
        return False

    if 'itu.int/' not in url:
        return False

    if not url.startswith('https://'):
        return False

    last_part = os.path.split(url)[-1]
    if '.' in last_part:
        ext = last_part.split('.')[-1]
        if ext not in ['html', 'aspx']:
            return False
    return True
