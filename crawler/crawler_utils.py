import json
import uuid


def write_json(data_load, json_path):
    with open(json_path, 'w', encoding='utf-8') as outfile:
        json.dump(data_load, outfile, indent=4, ensure_ascii=False)


def consider_sample(page_data):
    if not page_data:
        return False
    meta = page_data['meta']

    if meta['url'].split('.')[-1] in ['png', 'jpg', 'jpeg', 'xls', 'xlsx', 'xml', 'rm']:
        return False

    return True


def load_json(json_path):
    with open(json_path, encoding='utf-8') as json_file:
        return json.load(json_file)


def handler2hash(fn_handler):
    return uuid.uuid5(uuid.NAMESPACE_URL, fn_handler).hex


def parse_solr_response(sample, return_only_meta=False):
    def re_parse_solr(res):
        if not res:
            return {}

        return {
            'text': res['text'],
            'meta': {
                'title': res['meta']['title'],
                'uuid': handler2hash(res['meta']['id']),
                'url': res['meta']['source_file_url_s'],
                'type': res['meta']['type'],
                'web_handler': res['meta']['id'],
                'lang': res['meta']['lang'],
                'created_at': res['meta']['object_date_d'],
                'updated_at': res['meta']['object_date_d']

            }
        }

    data = dict()
    if not sample:
        return data

    if sample['id'].endswith('/cordra'):
        return data

    if '/file' in sample and len(sample['/file']) >= 1 and len(sample['/file'][0].strip()) > 0:
        text = sample['/file'][0]

    elif '/content_text_s' in sample and len(sample['/content_text_s']) >= 1 and sample['/content_text_s'][0].strip():
        text = sample['/content_text_s']
    elif '/subject_s' in sample and sample['/subject_s']:
        text = sample['/subject_s']
    else:
        text = ''

    if return_only_meta:
        text = ''

    lang = sample.get('/language_s', '')

    f_id = sample['id'] if 'id' in sample else sample['/identifier']

    # web_link_re = 'http://handle.itu.int/' + str(f_id)
    page_title = sample.get('/name_s', '')
    if sample.get('/subject_s', ''):
        page_title += '; ' + sample.get('/subject_s', '')

    # source_file_url_s = sample.get('/source_file_url_s', '')

    data = {
        'text': text,
        'meta': {
            'id': str(sample['id']),
            'lang': lang,
            'type': sample.get('type', ''),
            'source_file_url_s': sample.get('/source_file_url_s', ''),
            'responsible_group_s': sample.get('/responsible_group_s', ''),
            'object_type_s': sample.get('/object_type_s', ''),
            'object_state_s': sample.get('/object_state_s', ''),
            'object_date_d': sample.get('/object_date_d', ''),
            'collection_type_s': sample.get('/collection_type_s', ''),
            'web_link_re': 'http://handle.itu.int/' + str(sample['id']),
            'title': page_title
        }
    }
    data = re_parse_solr(data)
    return data
