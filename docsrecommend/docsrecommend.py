import redis
from redis.commands.search.field import VectorField
from redis.commands.search.query import Query

from sentence_transformers import SentenceTransformer
import uuid
import json
import numpy

# Run the example
# python3 -m pip install --upgrade pip
# pip install redis
# pip install sentence_transformers
# python3 docsrecommend.py

print("Get a connection to Redis")
pool = redis.ConnectionPool(host='127.0.0.1', port=6379, password='', encoding='utf-8', decode_responses=False)
conn = redis.Redis(connection_pool=pool)

print("Instantiate the SentenceTransformer object")
model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')


def importData():
    print("importData")
    # Open file with json documents (one json per line)
    docs = open('docs.json', 'r')
    lines = docs.readlines()

    for line in lines:
        data = json.loads(line)
        embedding = model.encode(data['content']).astype(numpy.float32).tobytes()
        data['content_embedding'] = embedding

        id = uuid.uuid1()
        conn.hset("newspaper:article:{}".format(id), mapping=data)

def createIndex():
    print("createIndex")
    # Create the index for Vector Similarity
    try:
        schema = (VectorField("content_embedding", "HNSW", {"TYPE": "FLOAT32", "DIM": 768, "DISTANCE_METRIC": "COSINE"}),)
        conn.ft('article_idx').create_index(schema)
    except:
        print("Index already exists") 

def getRecommendationsByCategory():
    print("getRecommendationsByCategory")
    # Let's iterate article by article in the database, and get 3 recommendations for every article
    cursor=0
    while True:
        cursor, keys  = conn.scan(cursor, match='newspaper:article*', count=100, _type="HASH")
        for key in keys:
            #print(str(key.split(':')[-1]))
            category = conn.hmget(key, ['category'])
            print("Similarities for an article from category:" + category[0])
            keys_and_args = [key]
            res = conn.eval("local vector = redis.call('hmget',KEYS[1], 'content_embedding') local searchres = redis.call('FT.SEARCH','article_idx','*=>[KNN 4 @content_embedding $B AS score]','PARAMS','2','B',vector[1], 'SORTBY', 'score', 'ASC', 'LIMIT', 1, 4,'RETURN',2,'score','category','DIALECT',2) return searchres", 1, *keys_and_args)

            # The first item is the number of returned results, we can skip it with [1:]
            for doc in res[1:]:
                print(doc)
            print()

        if (cursor==0):
            break

def getRecommendationsByText():
    print("getRecommendationsByText")

    embedding = model.encode("All articles about football").astype(numpy.float32).tobytes()
    q = Query("(*)=>[KNN 3 @content_embedding $B AS score]")\
        .return_field("content_embedding")\
        .return_field("title")\
        .sort_by("score", asc=True)\
        .dialect(2)
    res = conn.ft("article_idx").search(q, query_params={"B": embedding})
    it = iter(res.docs[0:])
    for x in it:
        print(f"---> id: {x['id']}")
        print(f"{type(x['content_embedding'])}")
        print(type(conn.hget(x['id'], "content_embedding")))
    


def cleanUp():
    print("cleanUp")
    try:
        conn.ft('article_idx').dropindex(delete_documents=False)
    except:
        print("Index did not exist") 

    cursor=0
    while True:
        cursor, keys  = conn.scan(cursor, match='newspaper:article*', count=100, _type="HASH")
        for key in keys:
            conn.delete(key)

        if (cursor==0):
            break


importData()
createIndex()
getRecommendationsByText()
cleanUp()