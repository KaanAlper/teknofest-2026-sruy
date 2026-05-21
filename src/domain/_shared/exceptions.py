"""Domain exception hiyerarşisi."""


class DomainError(Exception):
    """Tüm domain hata sınıflarının kökü."""


class InvalidPhaseTransition(DomainError):
    pass


class SafetyViolation(DomainError):
    pass


class RouteNotFound(DomainError):
    pass


class PlcProtocolError(DomainError):
    pass
