from main import app


def reverse(router_name: str, **kwargs) -> str:
    return app.url_path_for(router_name, **kwargs)
