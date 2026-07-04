"""ContextOS-specific exception hierarchy."""


class ContextOSError(Exception):
    """Base class for expected ContextOS application errors."""


class ConfigurationError(ContextOSError, ValueError):
    """Raised when configuration cannot be loaded or validated."""


class ReaderError(ContextOSError, OSError):
    """Raised when a reader cannot process a supported file."""


class ParserError(ContextOSError, ValueError):
    """Raised when parsing or chunking input fails."""


class CompressionError(ContextOSError, ValueError):
    """Raised when rule-based compression cannot complete."""


class RetrievalError(ContextOSError, ValueError):
    """Raised when lexical retrieval cannot complete."""


class MemoryError(ContextOSError, ValueError):
    """Raised when SQLite memory operations fail validation."""


class AdapterError(ContextOSError, RuntimeError):
    """Raised when an AI adapter cannot complete a request."""
