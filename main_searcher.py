from fastapi import FastAPI

from elastic_datastore import ElasticSearchManager
from graph_manager.graphy_manager import GraphManager

elastic_search_manager = ElasticSearchManager()
graph_manager = GraphManager()
app = FastAPI()


@app.get("/query")
async def query(q: str, cat: str, lang='en', top=50):
    filter_itu = {'type': [cat], 'lang': [lang]}
    res = elastic_search_manager.pipeline.run(
        query=q.lower(),
        params={
            "emb_Retriever": {"top_k": top},
            "bm25_Retriever": {'top_k': top},
            'filters': filter_itu
        }

    )
    pgs = [x.meta for x in res['documents']]
    urls = [x.meta.get('url') for x in res['documents']]

    if 'web'.lower() in cat.lower():
        g = graph_manager.get_graph(lang)
        pr = graph_manager.find_pr(g)
        ev = graph_manager.find_ev(g)
        pgs = {k: v for k, v in sorted({x: (pr.get(x.lower(), 0.0001) * ev.get(x.lower(), 0.0001) * pgs[
            x]) / graph_manager.get_distance_to_root(g, x.lower()) for x in urls}.items(), key=lambda item: item[1],
                                       reverse=True)}

    return pgs


@app.get("/")
async def root():
    return {'Hello': 'This is a semantic search engine!'}
