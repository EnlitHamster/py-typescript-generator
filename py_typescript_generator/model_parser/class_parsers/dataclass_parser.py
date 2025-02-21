from dataclasses import fields
from typing import Optional, Type

from py_typescript_generator.model.py_class import PyClass
from py_typescript_generator.model.py_field import PyField
from py_typescript_generator.model_parser.class_parsers.abstract_class_parser import (
    AbstractClassParser,
)
from py_typescript_generator.typing_utils.typing_utils import UnknownTypeError, get_type


class NotADataclassException(RuntimeError):
    def __init__(self, cls: Type):
        super(NotADataclassException, self).__init__(
            f"The class {cls} is not a dataclass."
        )


class DataclassParser(AbstractClassParser):
    def accepts_class(self, cls: Type) -> bool:
        try:
            fields(cls)
            return True
        except TypeError:
            return False

    def parse(self, cls: Type) -> PyClass:
        if not self.accepts_class(cls):
            raise NotADataclassException(cls)
        py_fields = []
        for field in fields(cls):
            typ: Optional[Type]
            field_type = field.type
            if isinstance(field_type, str):
                typ = get_type(field_type)

                if typ is None:
                    raise UnknownTypeError(field_type)
            elif isinstance(field_type, type):
                typ = field_type
            else:
                typ = type(field_type)

            py_fields.append(PyField(name=field.name, type=typ))

        return PyClass(name=cls.__name__, type=cls, fields=tuple(py_fields))
