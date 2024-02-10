from redis import Redis


class CacheCleaner:
    def __init__(self) -> None:
        self.redis = Redis(
            host='redis', port=6379, decode_responses=True, encoding='utf-8'
        )

    def get_redis_client(self) -> Redis:
        return self.redis

    def clear_main_cache(self) -> None:
        self.clear_cache('all_menus', 'all_submenus', 'all_dishes', 'all_menus_nested')

    def clear_cache(self, *args: str | list[str]) -> None:
        for key in args:
            self.redis.delete(str(key))


redis = CacheCleaner()
