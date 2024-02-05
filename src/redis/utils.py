from redis import Redis


def get_redis_client() -> Redis:
    return Redis(host='redis', port=6379, decode_responses=True, encoding='utf-8')


async def clear_main_cache(redis: Redis) -> None:
    redis.delete('all_menus')
    redis.delete('all_submenus')
    redis.delete('all_dishes')
