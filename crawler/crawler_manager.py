import json
import os

import requests
from tqdm import tqdm

from config import solr_base_url, tmp_solr_dict
from crawler.crawler_utils import handler2hash, parse_solr_response, write_json


class Crawler:
    def __init__(self):
        self.batch_size = 1000
        os.makedirs(tmp_solr_dict, exist_ok=True)

    def solr_crawler(self, start_idx):
        new_solr = []
        while True:
            res = requests.get(solr_base_url.format(self.batch_size, start_idx))
            res_json = json.loads(res.text)
            docs = res_json['response']['docs']
            if len(docs) == 0:
                break
            start_idx = start_idx + len(docs)
            for doc in tqdm(docs, f'Writing files of batch starting at {str(start_idx)} which contains '
                                  f'{len(docs)} entries'):
                fn = handler2hash(doc['id'])
                doc = parse_solr_response(doc)
                if os.path.exists(f'{tmp_solr_dict}/{fn}.json'):
                    continue
                new_solr.append(fn)
                write_json(data_load=doc, json_path=f'{tmp_solr_dict}/{fn}.json')
        return new_solr
