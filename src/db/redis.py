import redis.asyncio as redis

# Объект redis будет инициализирован позже
redis_client: redis.Redis = None


# Функция для получения подключения к Redis
async def get_redis() -> redis.Redis:
    return redis_client