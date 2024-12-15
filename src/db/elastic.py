from elasticsearch import AsyncElasticsearch, Elasticsearch

es: AsyncElasticsearch = None


# Функция понадобится при внедрении зависимостей
async def get_elastic() -> AsyncElasticsearch:
    return es


es = Elasticsearch("http://localhost:9200")

# Параметры для поиска по ID
index = "movies"
doc_id = "12afc5d5-af95-489b-801e-70cefa1b3ce5"

# Запрос для получения документа
response = es.get(index=index, id=doc_id)

# Вывод результата
print(response['_source'])