"""Application-specific exceptions.

``DatasetError`` and ``AnalysisError`` also derive from ``ValueError`` so code
that handles ``ValueError`` keeps working, while the API layer can map each
class to a precise HTTP status code.
"""


class AnimeAnalyticsError(Exception):
    """Base class for all application errors."""


class DatasetError(AnimeAnalyticsError, ValueError):
    """The dataset file is missing, unreadable, or does not match the schema."""


class DatasetUnavailableError(AnimeAnalyticsError):
    """A request needs the dataset but it was not loaded at startup."""


class AnalysisError(AnimeAnalyticsError, ValueError):
    """An analysis cannot be performed with the given parameters or data."""
