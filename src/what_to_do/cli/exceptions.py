"""CLI-specific exceptions"""


class CLIError(Exception): ...


class InvalidSettingsKeyError(CLIError):
    def __init__(self, key: str, available_keys: set[str]) -> None:
        self.key = key
        self.available_keys = available_keys

        super().__init__(
            f"No such setting found: {key}. "
            f"Available settings: {sorted(available_keys)}"
        )


class InvalidSettingsValueError(CLIError):
    def __init__(self, key: str, value: str, expected_type: object) -> None:

        self.key = key
        self.value = value
        self.expected_type = expected_type

        super().__init__(
            f"Invalid value for {key!r}: {value!r} "
            f"Value must be compatible with {expected_type}"
        )


class SettingsFileError(CLIError):
    pass
