import redis
from redis.cluster import RedisCluster
from redis.cluster import ClusterNode

from redis.commands.search.field import TextField, TagField, VectorField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition
from redis.commands.search.query import Query

# FT.CREATE doc_idx PREFIX 1 doc SCORE 1.0 SCHEMA content AS content TEXT WEIGHT 1.0
# FT.SEARCH doc_idx * WITHSCORES LIMIT 0 10


startup_nodes = [ClusterNode('127.0.0.1', 30001),
                ClusterNode('127.0.0.1', 30002),
                ClusterNode('127.0.0.1', 30003)]

rc = redis.RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

print(rc.ping)
print("Set: {}".format(rc.set("foo", "bar")))
print("Get: {}".format(rc.get("foo")))

try:
    index_def = IndexDefinition(prefix=["doc"])
    schema = (TextField("content", as_name="content"))
    rc.ft('doc_idx').create_index(schema, definition=index_def)
except:
    print("the index exists")

rc.hset("doc:1", mapping={"content": "un libro sui computer a 8 bit"})
rc.hset("doc:2", mapping={"content": "un libro di cucina"})
rc.hset("doc:3", mapping={"content": "un libro di elettronica"})

res = rc.ft('doc_idx').search(Query("*"))
print(res)
