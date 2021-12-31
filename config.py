import os

solr_base_url = 'http://dorepo.itu.int:8983/solr/cordra/query?q=*:*&wt=json&rows={}&start={}'

# save temporarily solr element until they are moved to ES
tmp_solr_dict = 'full_solr_index'

# a text file to save the uuid and web_handler of each item scraped from Solr so far.
es_items_path = 'mapping.txt'

# frequency of crawling Solr index.
sleep_time = 12 * 60 * 60  # 12 hours sleeping

elastic_instance_name = 'itu_se_new'

cat = {'ITU BaseTexts',
       'ITU Facebook',
       'ITU Flickr',
       'ITU News',
       'ITU Publications',
       'ITU Twitter',
       'ITU Youtube',
       'ITU-D Meeting Documents',
       'ITU-D Publications',
       'ITU-R Meeting Documents',
       'ITU-R Publications',
       'ITU-S Meeting Documents',
       'ITU-T Intellectual property rights',
       'ITU-T Liaison Statement',
       'ITU-T Meeting Documents',
       'ITU-T MeetingDocuments Folder',
       'ITU-T Publications',
       'ITU-T Recommendations',
       'ITU-T Standards Roadmap',
       'ITU-T Web Pages',
       'ITU-SG Web Pages',
       'ITU-D Web Pages',
       'ITU-R Web Pages',
       'ITU-T Work Item'}

langs = {'', '07', 'ar', 'en', 'es', 'fr', 'm', 'ru', 'sp', 'xx', 'zh'}

graph_root = 'graphs_pkl'
os.makedirs(graph_root, exist_ok=True)
graph_name = {
    'en': os.path.join(f'{graph_root}/web_en_graph.pkl'),
    'ar': os.path.join(f'{graph_root}/web_ar_graph.pkl'),
    'es': os.path.join(f'{graph_root}/web_es_graph.pkl'),
    'fr': os.path.join(f'{graph_root}/web_fr_graph.pkl'),
    'zh': os.path.join(f'{graph_root}/web_zh_graph.pkl'),
    'ru': os.path.join(f'{graph_root}/web_ru_graph.pkl')
}
