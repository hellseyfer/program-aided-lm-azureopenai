class OperationParameter():
    def __init__(self, name: str, paramType: str, description: str, required: bool, default_value = None):
        self.name = name
        self.type = paramType
        self.description = description
        self.required = required
        self.default_value = default_value


class TextOperationParameter(OperationParameter):
    def __init__(self, name: str, description: str, default_value: str = None, required: bool = False):
        super().__init__(name, "string", description, required, default_value)


class TextOptionsOperationParameter(OperationParameter):
    def __init__(self, name: str, description: str, possible_values: (str,), default_value: str = None, required: bool = False):
        super().__init__(name, "string", description, required, default_value)
        self.possible_values = possible_values


class NumberOperationParameter(OperationParameter):
    def __init__(self, name: str, description: str, default_value: int = None, required: bool = False):
        super().__init__(name, "number", description, required, default_value)


class NumberRangeOperationParameter(OperationParameter):
    def __init__(self, name: str, description: str, paramRange: (int, int), default_value: int = None, required: bool = False):
        super().__init__(name, "number", description, required, default_value)
        self.range = paramRange
