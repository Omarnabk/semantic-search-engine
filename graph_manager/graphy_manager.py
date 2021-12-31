import os
import pickle
from urllib.parse import urljoin, urlparse

import networkx as nx
import requests
import urllib3
from bs4 import BeautifulSoup

from config import graph_name
from graph_manager.graph_utils import is_valid_url, is_valid_url_structure, hash_url

urllib3.disable_warnings()

root_url = 'https://www.itu.int/en/Pages/default.aspx'.lower()
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


class GraphManager:
    def __init__(self):
        self.lang_mapping = {
            '': 'en',
            '07': 'en',
            'm': 'en',
            'xx': 'en',
            'en': 'en',
            'ar': 'ar',
            'es': 'es',
            'sp': 'es',
            'ru': 'ru',
            'zh': 'zh',
            'fr': 'fr',
        }

        if os.path.exists(graph_name['en']):
            g_en = pickle.load(open(graph_name['en'], 'rb'))
        else:
            g_en = nx.Graph(data=True)

        if os.path.exists(graph_name['es']):
            g_es = pickle.load(open(graph_name['es'], 'rb'))
        else:
            g_es = nx.Graph(data=True)

        if os.path.exists(graph_name['fr']):
            g_fr = pickle.load(open(graph_name['fr'], 'rb'))
        else:
            g_fr = nx.Graph(data=True)

        if os.path.exists(graph_name['ar']):
            g_ar = pickle.load(open(graph_name['ar'], 'rb'))
        else:
            g_ar = nx.Graph(data=True)

        if os.path.exists(graph_name['ru']):
            g_ru = pickle.load(open(graph_name['ru'], 'rb'))
        else:
            g_ru = nx.Graph(data=True)

        if os.path.exists(graph_name['zh']):
            g_zh = pickle.load(open(graph_name['zh'], 'rb'))
        else:
            g_zh = nx.Graph(data=True)

        self.dic_g = {
            'en': g_en,
            'ar': g_ar,
            'es': g_es,
            'ru': g_ru,
            'zh': g_zh,
            'fr': g_fr,
        }

    @staticmethod
    def get_distance_to_root(g, p):
        try:
            return nx.shortest_path_length(g, source=hash_url(root_url), target=hash_url(p.lower()))
        except:
            return 505

    @staticmethod
    def extract_hyperlinks(url):
        try:
            if not is_valid_url(url):
                return dict()
            internal_urls = set()

            r = requests.get(url, verify=False, headers=headers, timeout=10, allow_redirects=True)
            if r.status_code != 200:
                return []
            content = r.content
            if not is_valid_url(url):
                return []

            soup = BeautifulSoup(content, "html.parser")
            for a_tag in soup.findAll("a"):
                href = a_tag.attrs.get("href")
                if href == "" or href is None:
                    # href empty tag
                    continue
                # join the URL if it's relative (not absolute link)
                href = urljoin(url, href)
                parsed_href = urlparse(href)
                # remove URL GET parameters, URL fragments, etc.
                href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
                if not is_valid_url_structure(href):
                    # not a valid URL
                    continue
                if href in internal_urls:
                    # already in the set
                    continue
                internal_urls.add(href)

            internal_urls = list(set([urljoin(x, urlparse(x).path) for x in internal_urls]))
            return [x for x in internal_urls if is_valid_url(x)]
        except:
            return []

    @staticmethod
    def find_pr(g):
        pr = nx.pagerank(g, alpha=0.8, weight=g.edges(data=True))
        pr = {g.nodes(data=True)[e].get('url'): v for e, v in pr.items()}
        return pr

    @staticmethod
    def find_ev(g):
        ev = nx.eigenvector_centrality_numpy(g, weight=g.edges(data=True))
        ev = {g.nodes(data=True)[e].get('url'): v for e, v in ev.items()}
        return ev

    def get_graph(self, url_lang):
        return self.dic_g.get(url_lang, None)

    def append_item(self, src_url, url_lang):

        g = self.get_graph(url_lang=url_lang)
        if not is_valid_url(src_url):
            return g
        src_h = hash_url(src_url)
        if src_h in g.nodes():
            return g

        g.add_node(src_h)
        g.nodes[src_h]['url'] = src_url

        all_des = self.extract_hyperlinks(src_url)

        for des in all_des:
            if not is_valid_url(des):
                continue
            des = des.lower()
            des_h = hash_url(des)
            if des_h not in g.nodes():
                g.add_node(des_h)
                g.nodes[des_h]['url'] = des

            if g.has_edge(src_h, des_h):
                g.add_edge(src_h, des_h)
                g[src_h][des_h]['weight'] = g[src_h][des_h]['weight'] + 1
            else:
                g.add_edge(src_h, des_h)
                g[src_h][des_h]['weight'] = 1

        pickle.dump(g, open(graph_name[url_lang], 'wb'))

        return len(all_des)

# if __name__ == "__main__":
#     gm = GraphManager()
#     data = load_json('itud_web1.json')
#     for v in data.values():
#         src_url = v[0]
#         pg_type = v[1]
#         lang = gm.lang_mapping.get(v[2], 'en')
#         if is_valid_url(src_url):
#             added_nodes = gm.append_item(url_lang=lang, src_url=src_url)
#             print(src_url, added_nodes)
