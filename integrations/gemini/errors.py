class AIProviderError(RuntimeError):
    """Base class for normalized AI provider failures."""


class AIProviderTimeout(AIProviderError):
    pass


class AIProviderUnavailable(AIProviderError):
    pass


class AIRateLimited(AIProviderError):
    pass


class AIInvalidResponse(AIProviderError):
    pass


class AIRefusal(AIProviderError):
    pass


class AISafetyBlocked(AIProviderError):
    pass


class AIBudgetExceeded(AIProviderError):
    pass


class AIConfigurationError(AIProviderError):
    pass
