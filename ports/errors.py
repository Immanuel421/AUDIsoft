"""Gemeinsame Fehlerklassen an den technischen Port-Grenzen."""


class ClimateCubeError(Exception):
    """Basisklasse fuer erwartete, behandelbare Systemfehler."""


class ConfigurationError(ClimateCubeError):
    pass


class ClockError(ClimateCubeError):
    pass


class StorageError(ClimateCubeError):
    pass


class StorageMigrationError(StorageError):
    pass


class RadioError(ClimateCubeError):
    pass
