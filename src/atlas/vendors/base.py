from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

from sqlalchemy.ext.asyncio import AsyncEngine

if TYPE_CHECKING:
    from atlas.data.config import Parameters, Service
    from atlas.data.types import TaskDetails

__all__ = (
    "SecretsManager",
    "QueueManager",
    "DatabaseManager",
    "ExecutorService",
    "ConsumerCallback",
    "QueueEvent",
)


class SecretsManager:
    _name: Service = "SECRETS"

    def get_credentials(self, id: str, **kwargs) -> dict[str, str]:
        raise NotImplementedError


class ConsumerCallback(Protocol):
    """
    Protocol that a consumer callback of a queue must follow.

    A valid callback coroutine must accept,

    body: message payload (str)
    event: object that wraps actual vendor message.

    """

    async def __call__(self, body: bytes, event: QueueEvent, **kwds: Any) -> Any: ...


class QueueEvent:
    def __init__(self, message: Any, **kwds) -> None:
        self._message = message

    @property
    def message(self) -> Any:
        return self._message


class QueueManager:
    _name: Service = "QUEUE"

    def __init__(self, params: "Parameters") -> None:
        self.params = params

    async def apublish(self, message: dict[str, Any], queue_name: str, **kwargs) -> None:
        raise NotImplementedError

    async def aconsume(
        self, queue_mapping: dict[str, ConsumerCallback], **kwargs
    ) -> None:
        raise NotImplementedError

    async def aclose(self) -> None:
        raise NotImplementedError


class DatabaseManager:
    def __init__(self, params: "Parameters") -> None:
        self.params = params

    _name: Service = "DATABASE"

    @property
    def aengine(self) -> AsyncEngine:
        raise NotImplementedError

    async def aclose(self) -> None:
        """tries to close database resources gracefully

        Raises: No exception will be raised
        """
        raise NotImplementedError


class ExecutorService:
    def __init__(self, params: "Parameters") -> None:
        self.params = params

    _name: Service = "EXECUTOR"

    async def asubmit_task(self, task_details: "TaskDetails", **kwargs) -> None:
        raise NotImplementedError
