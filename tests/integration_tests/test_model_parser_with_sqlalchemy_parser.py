from dataclasses import dataclass
from typing import List, Dict

from ordered_set import OrderedSet
from sqlalchemy import String

from py_typescript_generator.model.model import Model
from py_typescript_generator.model.py_class import PyClass
from py_typescript_generator.model.py_field import PyField
from py_typescript_generator.model_parser.class_parsers.sqlalchemy_parser import (
    SQLAlchemyParser,
)
from py_typescript_generator.model_parser.model_parser import (
    ModelParser,
    ModelParserSettings,
)

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MySimpleModel(Base):
    __tablename__ = 'my_simple_model'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(String(length=100), nullable=False)


def test_should_parse_simple_model_correctly():
    model_parser = ModelParser(
        [MySimpleModel], [SQLAlchemyParser()], ModelParserSettings()
    )

    model = model_parser.parse()

    assert model == Model(
        classes=OrderedSet(
            [
                PyClass(
                    name="MySimpleModel",
                    type=MySimpleModel,
                    fields=(
                        PyField(name="id", type=int),
                        PyField(name="text", type=str),
                    ),
                )
            ]
        )
    )