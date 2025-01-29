import os
from hypurrquant_fastapi_core.logging_config import configure_logging

logger = configure_logging(__file__)


class Singleton(type):
    """
    싱글톤 메타클래스:
    해당 메타클래스를 사용하는 클래스는 인스턴스가 하나만 생성됨.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def singleton(cls):
    """
    클래스 데코레이터를 사용하여 싱글톤 패턴을 구현합니다.
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
