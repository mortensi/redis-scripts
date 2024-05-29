from redis.commands.search.query import Query
from redis.commands.search.field import TextField, TagField, VectorField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
import redis


r = redis.Redis(host="localhost", port=6379, protocol=2, decode_responses=True)

indexes = r.execute_command("FT._LIST")

try:
    r.ft("doc_idx").dropindex(delete_documents=True)
except:
    pass

index_def = IndexDefinition(prefix=["doc:"], index_type=IndexType.HASH)
schema = (  TagField("category", as_name="category"),
            TagField("title", as_name="title"),
            NumericField("updated", as_name="updated"),
            TextField("content", as_name="content", weight=1.5))
r.ft('doc_idx').create_index(schema, definition=index_def)

r.hset("doc:1", mapping={"content" : "a book about 8 bits computers", "title":"About computers"})
r.hset("doc:2", mapping={"content" : "a book about cooking", "title":"About cooking"})
r.hset("doc:3", mapping={"content" : "A book about electronics", "title":"About electronics"})

res = r.ft("doc_idx").search(Query("cooking"))
#print(res)

# using JSON

r = redis.Redis(host="localhost", port=6379, protocol=2, decode_responses=True)

try:
    r.ft("doc_json_idx").dropindex(delete_documents=True)
except:
    pass

index_def = IndexDefinition(prefix=["json:"], index_type=IndexType.JSON)
schema = (  TagField("$.category", as_name="category"),
            TagField("$.title", as_name="title"),
            NumericField("$.updated", as_name="updated"),
            TextField("$.content", as_name="content", weight=1.5))
r.ft('doc_json_idx').create_index(schema, definition=index_def)

r.json().set("json:1", "$", {"content" : "a book about 8 bits computers", "title":"About computers"})
r.json().set("json:2", "$", {"content" : "a book about cooking", "title":"About cooking"})
r.json().set("json:3", "$", {"content" : "A book about electronics", "title":"About electronics"})

res = r.ft("doc_json_idx").search(Query("cooking"))
#print(res)

# ---------------------------------

r = redis.Redis(host="localhost", port=6379, protocol=2, decode_responses=True)

r.delete("names")
r.json().set("names", "$", {})
r.json().set("names", "$.list", [])
r.json().arrappend("names", "$.list", {"mirko": 47})
r.json().arrappend("names", "$.list", {"ana": 45})
res = r.json().get("names")

print(res)

r = redis.Redis(host="localhost", port=6379, protocol=3, decode_responses=True)

res = r.json().get("names")
#print(res)



from rejson import Client, Path
res = ["John", "Doe", "Jane"]
r.jsonset("mykey", Path.rootPath(), res)