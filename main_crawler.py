import os
import time

from tqdm import tqdm

from config import es_items_path, sleep_time, tmp_solr_dict
from crawler.crawler_manager import Crawler
from crawler.crawler_utils import consider_sample, load_json
from elastic_datastore import ElasticSearchManager
from graph_manager.graph_utils import is_valid_url
from graph_manager.graphy_manager import GraphManager

if __name__ == "__main__":
    crawler = Crawler()
    graph_manager = GraphManager()
    es_manager = ElasticSearchManager()

    while True:
        if os.path.exists(es_items_path):
            with open(es_items_path)as rdr:
                es_exists = [x.strip().split('\t')[0] for x in rdr.readlines()]
                es_exists = list(set(es_exists))
        else:
            es_exists = []
        print(f'Existing length {len(es_exists)}')

        print('Start scraping solr')
        new_solr = crawler.solr_crawler(start_idx=len(es_exists))
        print(f'new from solar {len(new_solr)}')

        to_add = set(new_solr).difference(es_exists)
        print(f'new to add {len(to_add)}')

        if not to_add:
            print('Nothing to add yet. I will check tomorrow!')
            time.sleep(sleep_time)
            continue

        wrt = open(es_items_path, 'a')
        for item in tqdm(to_add, 'Inserting to ES'):
            if not os.path.exists(os.path.join(tmp_solr_dict, item + '.json')):
                wrt.write(f'{item}\t{0}\t{item}\n')
                continue
            slr = load_json(os.path.join(tmp_solr_dict, item + '.json'))
            if not slr:
                wrt.write(f'{item}\t{0}\t{item}\n')
                continue
            uuid = slr['meta'].get('uuid')
            handler = slr['meta'].get('web_handler')
            if not consider_sample(slr):
                wrt.write(f'{uuid}\t{0}\t{handler}\n')
                continue
            inserted = es_manager.insert_item_elastic(slr)
            if inserted:
                wrt.write(f'{uuid}\t{1}\t{handler}\n')
            else:
                wrt.write(f'{uuid}\t{0}\t{handler}\n')
            os.remove(os.path.join(tmp_solr_dict, item + '.json'))

            # update the graph:
            src_url = slr['meta'].get('url')
            url_lang = slr['meta'].get('lang')
            if is_valid_url(src_url):
                graph_manager.append_item(src_url=src_url, url_lang=url_lang)

        print('Start updating elastic')
        es_manager.update_item_elastic()
        wrt.close()

        print('Start sleeping')
        time.sleep(sleep_time)
