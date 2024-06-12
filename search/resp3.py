from redis.commands.search.query import Query
from redis.commands.search.field import TextField, TagField, VectorField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
import redis


r = redis.Redis(host="localhost", port=6379, protocol=2, decode_responses=True)

indexes = r.execute_command("FT._LIST")

try:
    r.ft("document_idx").dropindex(delete_documents=True)
except:
    pass

index_def = IndexDefinition(prefix=["document:"], index_type=IndexType.HASH)
schema = (  TagField("category", as_name="category"),
            TagField("title", as_name="title"),
            NumericField("updated", as_name="updated"),
            TextField("content", as_name="content", weight=1.5))
r.ft('document_idx').create_index(schema, definition=index_def)

r.hset("document:1", mapping={"content" : "a book about 8 bits computers", "title":"About computers"})
r.hset("document:2", mapping={"content" : "a book about cooking", "title":"About cooking"})
r.hset("document:3", mapping={"content" : "A book about electronics", "title":"About electronics"})

res = r.ft("document_idx").search(Query("cooking"))
print(res)

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
print(res)




