
class ElasticQueryBuilder:
    @staticmethod
    def match(field: str, query: str, fuzziness: str = "AUTO") -> dict:
        return {
            "match": {
                field: {
                    "query": query,
                    "fuzziness": fuzziness,
                }
            }
        }

    @staticmethod
    def nested(path: str, query: dict) -> dict:
        return {
            "nested": {
                "path": path,
                "query": query
            }
        }

    @staticmethod
    def bool_query(must: list = None, should: list = None, filter_: list = None) -> dict:
        return {
            "bool": {
                "must": must or [],
                "should": should or [],
                "filter": filter_ or [],
            }
        }

    @staticmethod
    def term(field: str, value: str) -> dict:
        return {
            "term": {
                field: value
            }
        }