import os
from hypurrquant_fastapi_core.logging_config import configure_logging
from typing import Type, Dict, Any, TypeVar

T = TypeVar("T")

logger = configure_logging(__name__)


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


class SingletonRegistry:
    _instances: Dict[Type[Any], Any] = {}

    @classmethod
    def get_instance(cls, klass: Type[T], *args, **kwargs) -> T:
        # 이미 생성된 인스턴스가 있으면 바로 반환
        if klass in cls._instances:
            return cls._instances[klass]
        # 없으면 동적으로 klass(*args, **kwargs) 호출해 생성
        inst = klass(*args, **kwargs)
        cls._instances[klass] = inst
        return inst
