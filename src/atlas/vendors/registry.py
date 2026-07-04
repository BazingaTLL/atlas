from __future__ import annotations

import copy
import importlib
import logging
import pkgutil
from typing import cast

import atlas.vendors as vendors

__all__ = ("VendorRegistry",)

logger = logging.getLogger(__name__)


class VendorRegistry:
    __REGISTRY = {}
    __SUPPORTS_METHOD = "supports"

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        supports = getattr(cls, VendorRegistry.__SUPPORTS_METHOD, None)
        if not supports or not callable(supports):
            raise TypeError(
                "Class `{}` must implement a staticmethod `{}`".format(
                    cls.__name__, VendorRegistry.__SUPPORTS_METHOD
                )
            )
        vendor, service = cast(tuple[str, str], supports())
        vendor, service = vendor.lower(), service.lower()

        if vendor in VendorRegistry.__REGISTRY:
            if service in VendorRegistry.__REGISTRY[vendor]:
                existing_cls = VendorRegistry.__REGISTRY[vendor][service]
                raise ValueError(
                    "Both `{}` and `{}` claim to support {}:{}".format(
                        cls.__name__, existing_cls.__name__, vendor, service
                    )
                )
        else:
            VendorRegistry.__REGISTRY[vendor.lower()] = {}
        VendorRegistry.__REGISTRY[vendor.lower()][service.lower()] = cls

    @staticmethod
    def get_vendor_registry() -> dict:
        return copy.deepcopy(VendorRegistry.__REGISTRY)

    @classmethod
    def create(cls, vendor: str, service: str, *args, **kwargs):
        try:
            target_class = cls.__REGISTRY[vendor.lower()][service.lower()]
            return target_class(*args, **kwargs)
        except Exception as err:
            raise ValueError(
                "Failed to create object for {}:{}".format(vendor, service)
            ) from err


# [TODO] Implement lazy loading.
def register_vendors() -> None:
    package_name = vendors.__name__

    for _, module_name, _ in pkgutil.iter_modules(vendors.__path__):
        module_path = f"{package_name}.{module_name}"
        try:
            importlib.import_module(module_path)
        except Exception as e:
            logger.warning(f"Failed to register vendor {module_path}: {e}")

    logger.debug(
        "Registered Vendor info - {}".format(VendorRegistry.get_vendor_registry())
    )
