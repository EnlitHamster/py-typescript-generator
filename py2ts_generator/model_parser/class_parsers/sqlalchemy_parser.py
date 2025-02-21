from typing import List, Type

from sqlalchemy import Column
import sqlalchemy.inspection
from sqlalchemy.sql.type_api import TypeEngine

from py2ts_generator.model.py_class import PyClass
from py2ts_generator.model.py_field import PyField
from py2ts_generator.model_parser.class_parsers.abstract_class_parser import (
    AbstractClassParser,
)
from py2ts_generator.typing_utils.typing_utils import UnknownTypeError


class NotASQLAlchemyModelException(RuntimeError):
    def __init__(self, cls: Type):
        super(NotASQLAlchemyModelException, self).__init__(
            f"The class {cls} is not a SQLAlchemy model."
        )


class SQLAlchemyParser(AbstractClassParser):
    def accepts_class(self, cls: Type) -> bool:
        try:
            sqlalchemy.inspection.inspect(cls)
            return True
        except TypeError:
            return False

    def parse(self, cls: Type) -> PyClass:
        if not self.accepts_class(cls):
            raise NotASQLAlchemyModelException(cls)

        fields: List[PyField] = []
        inspector = sqlalchemy.inspection.inspect(cls)

        for col in inspector.columns:
            if not isinstance(col, Column):
                raise UnknownTypeError(type(col).__name__)

            typ: Type
            if isinstance(col.type, TypeEngine):
                typ = col.type.python_type
            else:
                typ = col.type

            fields.append(PyField(name=col.name, type=typ))

        return PyClass(name=cls.__name__, type=cls, fields=tuple(fields))
