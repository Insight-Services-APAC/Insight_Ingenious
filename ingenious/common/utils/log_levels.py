class LogLevel:
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    @staticmethod
    def from_string(level_str: str):
        level_mapping = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
        }
        return level_mapping.get(str(level_str).upper(), None)

    @staticmethod
    def to_string(level):
        level_mapping = {
            LogLevel.DEBUG: "DEBUG",
            LogLevel.INFO: "INFO",
            LogLevel.WARNING: "WARNING",
            LogLevel.ERROR: "ERROR",
        }
        return level_mapping.get(level, "Unknown")
