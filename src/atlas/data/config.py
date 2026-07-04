from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Literal, cast

logger = logging.getLogger(__name__)

ATLAS_HOME = os.environ.get("ATLAS_HOME", "")

PARAM_VENDOR = "vendor"
PARAM_OPTIONS = "options"
PARAM_DATABASE_NAME = "dbName"
PARAM_SCHEMA = "schema"
PARAM_URL = "url"
PARAM_HOST = "host"
PARAM_PORT = "port"
PARAM_USERNAME = "user"
PARAM_PASSWORD = "password"
PARAM_SECRET_ID = "id"

Service = Literal["SECRETS", "QUEUE", "DATABASE", "EXECUTOR"]


class Parameters:
    def __init__(self, config: dict[str, Any]) -> None:
        self._secrets_config = config.get("secrets", {})
        self._db_config = config.get("database", {})
        self._queue_config = config.get("queue", {})
        self._executor_config = config.get("executor", {})
        self.__ref_data: dict[str, str] | None = None

    def _get_secrets(self) -> dict[str, str]:
        from atlas.vendors.base import SecretsManager
        from atlas.vendors.registry import VendorRegistry

        vendor = self._secrets_config.get(PARAM_VENDOR)
        id = self._secrets_config.get("id")
        options = self._secrets_config.get("options", {})
        if not vendor or not id:
            return {}
        manager = cast(SecretsManager, VendorRegistry.create(vendor, "secrets"))
        return manager.get_credentials(id, **options)

    def resolve_ref(self, value: str) -> str:
        pattern = r"\$\{secrets\.(\w+)\}"

        def get_ref_value(match: re.Match):
            if self.__ref_data is None:
                self.__ref_data = self._get_secrets()
            key = match.group(1)
            return str(self.__ref_data.get(key, match.group(0)))

        return re.sub(pattern, get_ref_value, value)

    def conf_value(self, config: dict[str, Any], param: str) -> str:
        value = cast(str, config[param])
        if value:
            value = self.resolve_ref(value)
        return value

    @property
    def database_name(self) -> str:
        name = os.environ.get("ATLAS_DATABASE_NAME")
        if not name:
            name = self.resolve_ref(self._db_config[PARAM_DATABASE_NAME])
        return name

    @property
    def database_schema(self) -> str:
        schema = os.environ.get("ATLAS_DATABASE_SCHEMA")
        if not schema:
            schema = self.resolve_ref(self._db_config[PARAM_SCHEMA])
        return schema

    @property
    def database_user(self) -> str:
        user = os.environ.get("ATLAS_DATABASE_USER")
        if not user:
            user = self.conf_value(self._db_config, PARAM_USERNAME)
        return user

    @property
    def database_password(self) -> str:
        pwd = os.environ.get("ATLAS_DATABASE_PASSWORD")
        if not pwd:
            pwd = self.conf_value(self._db_config, PARAM_PASSWORD)
        return pwd

    @property
    def database_host(self) -> str:
        url = os.environ.get("ATLAS_DATABASE_HOST")
        if not url:
            url = self.conf_value(self._db_config, PARAM_HOST)
        return url

    @property
    def database_port(self) -> int:
        url = os.environ.get("ATLAS_DATABASE_PORT")
        if not url:
            url = self.conf_value(self._db_config, PARAM_PORT)
        return int(url)

    @property
    def database_options(self) -> dict[str, Any]:
        return self._db_config.get(PARAM_OPTIONS, {})

    @property
    def database_vendor(self) -> str:
        return self._db_config[PARAM_VENDOR]

    @property
    def executor_vendor(self) -> str:
        return self._executor_config[PARAM_VENDOR]

    @property
    def executor_options(self) -> dict[str, Any]:
        return self._executor_config.get(PARAM_OPTIONS, {})

    @property
    def queue_vendor(self) -> str:
        return self._queue_config[PARAM_VENDOR]

    @property
    def queue_url(self) -> str:
        url = os.environ.get("ATLAS_QUEUE_URL")
        if not url:
            url = self.conf_value(self._queue_config, PARAM_URL)
        return url

    @property
    def queue_options(self) -> dict[str, Any]:
        return self._queue_config.get(PARAM_OPTIONS, {})


_params_instance: Parameters | None = None


# [TODO] Have config schema validation
def get_config() -> dict[str, Any]:
    config_path = os.path.join(ATLAS_HOME, "config.json")
    logger.debug(f"Loading config from, {config_path}")
    try:
        with open(config_path, "r") as fd:
            config_str = fd.read()
        return cast(dict[str, Any], json.loads(config_str))
    except Exception as _:
        return {}


def get_parameters() -> Parameters:
    """Get the singleton Parameters instance."""
    global _params_instance
    if _params_instance is None:
        _params_instance = Parameters(get_config())
    return _params_instance
