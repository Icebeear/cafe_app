from redis import Redis


def get_redis_client() -> Redis:
    return Redis(host='localhost', port=6379, decode_responses=True, encoding='utf-8')
