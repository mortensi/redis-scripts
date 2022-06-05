local vector = redis.call('hmget',KEYS[1], 'content_embedding')

local searchres = redis.call('FT.SEARCH','article_idx','*=>[KNN 4 @content_embedding $B AS score]','PARAMS','2','B',vector[1], 'SORTBY', 'score', 'ASC', 'LIMIT', 1, 4,'RETURN',2,'title','category','DIALECT',2)

return searchres
