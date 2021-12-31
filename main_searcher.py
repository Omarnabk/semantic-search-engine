import uvicorn
from fastapi import FastAPI

from elastic_datastore import ElasticSearchManager
# from graph_manager.graph_manager import GraphManager

elastic_search_manager = ElasticSearchManager()
# graph_manager = GraphManager()
app = FastAPI()


@app.get("/query")
async def query(q: str, cat: str, lang='en', top=50):
    filter_itu = {'type': [cat], 'lang': [lang]}
    res = elastic_search_manager.pipeline.run(
        query=q.lower(),
        params={
            "emb_Retriever": {"top_k": 1000},
            "bm25_Retriever": {'top_k': 1000},
            'filters': filter_itu
        }

    )
    new_pgs = []
    new_meta = []
    for x in res['documents']:
        u = x.meta.get('url', '')
        if u not in new_pgs:
            new_pgs.append(x.meta['url'])
            new_meta.append(x.meta)
    new_meta = sorted(new_meta, key=lambda d: d['created_at'], reverse=True)
    return new_meta[:top]

    # if 'web'.lower() in cat.lower():
    #     urls = [x.meta.get('url') for x in res['documents']]
    #     g_obj = graph_manager.get_graph(lang)
    #     g_res = {k: v for k, v in sorted({x: (g_obj.pr.get(x.lower(), 0.0001) * g_obj.ev.get(x.lower(), 0.0001) * urls.index(x)) / graph_manager.get_distance_to_root(g_obj.g, x.lower()) for x in urls}.items(),
    #                                      key=lambda item: item[1],
    #                                      reverse=True)}

    # return pgs


@app.get("/")
async def root():
    return {'Hello': 'This is a semantic search engine!'}


if __name__ == "__main__":
    uvicorn.run("main_searcher:app", host="0.0.0.0", port=8989, log_level="info")
