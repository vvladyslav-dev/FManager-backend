from typing import Protocol, TypeVar

TRequest = TypeVar('TRequest', contravariant=True)
TResponse = TypeVar('TResponse', covariant=True)


class UseCase(Protocol[TRequest, TResponse]):
    """Base interface for use cases."""
    
    async def handle(self, request: TRequest) -> TResponse:
        """Execute the use case."""
        ...

