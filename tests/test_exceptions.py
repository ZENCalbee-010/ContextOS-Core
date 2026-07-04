from contextos.ai_adapter import AIAdapterError
from contextos.exceptions import (
    AdapterError,
    CompressionError,
    ContextOSError,
    MemoryError,
    ParserError,
    ReaderError,
    RetrievalError,
)


def test_contextos_exception_hierarchy() -> None:
    assert issubclass(ReaderError, ContextOSError)
    assert issubclass(ParserError, ContextOSError)
    assert issubclass(CompressionError, ContextOSError)
    assert issubclass(RetrievalError, ContextOSError)
    assert issubclass(MemoryError, ContextOSError)
    assert issubclass(AdapterError, ContextOSError)
    assert issubclass(AIAdapterError, AdapterError)
