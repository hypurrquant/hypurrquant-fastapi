import os
from hypurrquant_fastapi_core.logging_config import configure_logging
from typing import Type, Dict, Any, TypeVar
import threading

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
    """
    Interface-to-implementation mapping with singleton instance management.
    """

    _instances: Dict[Type[Any], Any] = {}
    _impl_map: Dict[Type[Any], Type[Any]] = {}
    _lock = threading.Lock()

    @classmethod
    def register_implementation(cls, interface: Type[T], impl: Type[T]) -> None:
        """
        Register a concrete implementation for an interface.
        """
        with cls._lock:
            cls._impl_map[interface] = impl

    @classmethod
    def get_instance(cls, interface: Type[T], *args, **kwargs) -> T:
        """
        Retrieve or create the singleton for the given interface.
        If an implementation was registered, uses that; otherwise assumes interface is concrete.
        """
        with cls._lock:
            # Determine the concrete class
            concrete = cls._impl_map.get(interface, interface)
            # If already instantiated, return it
            if concrete in cls._instances:
                return cls._instances[concrete]
            # Instantiate and store
            instance = concrete(*args, **kwargs)
            cls._instances[concrete] = instance
            return instance
