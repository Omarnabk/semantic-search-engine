from haystack import Pipeline
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.nodes import ElasticsearchRetriever, JoinDocuments
from haystack.preprocessor.preprocessor import PreProcessor
from haystack.retriever.dense import EmbeddingRetriever

from config import elastic_instance_name
from logger import DisableLogger
from preprocessor import clean_text


class ElasticSearchManager:
    def __init__(self):
        self.document_store_es = ElasticsearchDocumentStore(host="localhost",
                                                            similarity='cosine',
                                                            index=elastic_instance_name,
                                                            embedding_field='embedding',
                                                            search_fields='text',
                                                            name_field='title',
                                                            embedding_dim=512
                                                            )

        self.preprocessor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            split_by="word",
            split_length=512,
            split_respect_sentence_boundary=True,
            language='en'
        )

        self.emb_retriever = EmbeddingRetriever(
            self.document_store_es,
            embedding_model='sentence-transformers/distiluse-base-multilingual-cased-v1',
            model_format='sentence_transformers',
            use_gpu=True,
        )

        self.bm25_retriever = ElasticsearchRetriever(self.document_store_es)

        self.pipeline = Pipeline()
        self.pipeline.add_node(component=self.bm25_retriever, name="bm25_Retriever", inputs=["Query"])
        self.pipeline.add_node(component=self.emb_retriever, name="emb_Retriever", inputs=["Query"])
        self.pipeline.add_node(component=JoinDocuments(join_mode="merge", weights=[0.5, 0.8]), name="JoinResults",
                               inputs=["bm25_Retriever", "emb_Retriever"])

    def split_response(self, dicts):
        docs = [self.preprocessor.process(d) for d in dicts if d['text']]
        flattened_docs = [d for list_of_dicts in docs for d in list_of_dicts]
        return flattened_docs

    def get_count_es(self, web_handler):
        try:
            return self.document_store_es.get_metadata_values_by_key('web_handler',
                                                                     filters={
                                                                         'web_handler': [f'{web_handler}']
                                                                     })[0]['count']
        except:
            return 0

    def insert_item_elastic(self, solr_item):
        try:
            solr_item['text'] = clean_text(solr_item['text'])
            if not solr_item['text']:
                return False

            pages_batch_splits = self.split_response([solr_item])
            with DisableLogger():
                self.document_store_es.write_documents(pages_batch_splits)
                return True
        except:
            return False

    def delete_item_elastic(self, web_handler=None, uuid=None):
        if web_handler:
            self.document_store_es.delete_documents(filters={'web_handler': [web_handler]})
        if uuid:
            self.document_store_es.delete_documents(filters={'uuid': [uuid]})

    def update_item_elastic(self):
        self.document_store_es.update_embeddings(retriever=self.emb_retriever,
                                                 index=elastic_instance_name,
                                                 update_existing_embeddings=False
                                                 )
