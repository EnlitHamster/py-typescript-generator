from enum import Enum
from typing import Dict

import pytest
from ordered_set import OrderedSet

from py2ts_generator.model.model import Model
from py2ts_generator.model.py_class import PyClass
from py2ts_generator.model.py_enum import PyEnum, PyEnumValue
from py2ts_generator.model.py_field import PyField
from py2ts_generator.typescript_model_compiler.ts_field import TsField
from py2ts_generator.typescript_model_compiler.ts_model import TsModel
from py2ts_generator.typescript_model_compiler.ts_object_type import (
    TsObjectType,
    TsDiscriminator,
    TsUnionType,
)
from py2ts_generator.typescript_model_compiler.ts_type import TsType
from py2ts_generator.typescript_model_compiler.typescript_model_compiler import (
    TypescriptModelCompiler,
    UnsupportedKeyTypeForMappedType,
    UnsupportedEnumValue,
    TypescriptModelCompilerSettings,
    CaseFormat,
)
from py2ts_generator.typescript_model_compiler.well_known_types import TS_STRING
from tests.unittests.fixture_classes import ClassFixture, EnumFixture


def _compile_py_class(py_class: PyClass) -> TsModel:
    model = Model.of_classes([py_class])
    model_compiler = TypescriptModelCompiler(TypescriptModelCompilerSettings())
    ts_model = model_compiler.compile(model)
    return ts_model


def _compile_py_enum(py_enum: PyEnum) -> TsModel:
    model = Model(enums=OrderedSet([py_enum]))
    model_compiler = TypescriptModelCompiler(TypescriptModelCompilerSettings())
    ts_model = model_compiler.compile(model)
    return ts_model


def test_should_compile_empty_class(empty_class):
    ts_model = _compile_py_class(empty_class.py_class)

    assert ts_model == TsModel.of_types([empty_class.ts_object_type])


def test_should_compile_class_with_empty_class(class_with_empty_class):
    ts_model = _compile_py_class(class_with_empty_class.py_class)

    assert ts_model == TsModel.of_types([class_with_empty_class.ts_object_type])


def test_should_compile_class_with_class_with_empty_class(
    class_with_class_with_empty_class,
):
    ts_model = _compile_py_class(class_with_class_with_empty_class.py_class)

    assert ts_model == TsModel.of_types(
        [class_with_class_with_empty_class.ts_object_type]
    )


def test_should_compile_classes_with_cycle(first_class_in_cycle, second_class_in_cycle):
    model = Model.of_classes(
        [first_class_in_cycle.py_class, second_class_in_cycle.py_class]
    )
    model_compiler = TypescriptModelCompiler(TypescriptModelCompilerSettings())

    ts_model = model_compiler.compile(model)

    assert ts_model == TsModel.of_types(
        [first_class_in_cycle.ts_object_type, second_class_in_cycle.ts_object_type]
    )


@pytest.mark.parametrize(
    "fixture_name",
    [
        "class_with_int",
        "class_with_str",
        "class_with_float",
        "class_with_bool",
        "class_with_bytes",
        "class_with_datetime",
        "class_with_uuid",
    ],
)
def test_should_compile_class_with_scalar_types(fixture_name, request):
    class_fixture = request.getfixturevalue(fixture_name)
    ts_model = _compile_py_class(class_fixture.py_class)

    assert ts_model == TsModel.of_types([class_fixture.ts_object_type])


def test_should_compile_class_with_optional_int(class_with_optional_int):
    ts_model = _compile_py_class(class_with_optional_int.py_class)

    assert ts_model == TsModel.of_types([class_with_optional_int.ts_object_type])


def test_should_compile_class_with_optional_empty_class(
    class_with_optional_empty_class,
):
    ts_model = _compile_py_class(class_with_optional_empty_class.py_class)

    assert ts_model == TsModel.of_types(
        [class_with_optional_empty_class.ts_object_type]
    )


class TestTypesMappedToArray:
    def test_should_compile_class_with_str_list(self, class_with_str_list):
        ts_model = _compile_py_class(class_with_str_list.py_class)

        assert ts_model == TsModel.of_types([class_with_str_list.ts_object_type])

    def test_should_compile_class_with_empty_class_list(
        self, class_with_empty_class_list
    ):
        ts_model = _compile_py_class(class_with_empty_class_list.py_class)

        assert ts_model == TsModel.of_types(
            [class_with_empty_class_list.ts_object_type]
        )

    def test_should_compile_class_with_str_set(self, class_with_str_set):
        ts_model = _compile_py_class(class_with_str_set.py_class)

        assert ts_model == TsModel.of_types([class_with_str_set.ts_object_type])

    def test_should_compile_class_with_str_frozen_set(self, class_with_str_frozen_set):
        ts_model = _compile_py_class(class_with_str_frozen_set.py_class)

        assert ts_model == TsModel.of_types([class_with_str_frozen_set.ts_object_type])

    def test_should_compile_class_with_str_ordered_set(
        self, class_with_str_ordered_set
    ):
        ts_model = _compile_py_class(class_with_str_ordered_set.py_class)

        assert ts_model == TsModel.of_types([class_with_str_ordered_set.ts_object_type])

    def test_should_compile_class_with_optional_empty_class(
        self, class_with_optional_empty_class: ClassFixture
    ) -> None:
        ts_model = _compile_py_class(class_with_optional_empty_class.py_class)

        assert ts_model == TsModel.of_types(
            [class_with_optional_empty_class.ts_object_type]
        )


class TestTypesMappedToObject:
    def test_should_fail_if_key_type_is_not_str(self):
        class ClassWithIntStrDict:
            pass

        py_class = PyClass(
            name="ClassWithIntStrDict",
            type=ClassWithIntStrDict,
            fields=(PyField(name="int_dict", type=Dict[int, str]),),
        )
        with pytest.raises(UnsupportedKeyTypeForMappedType):
            _compile_py_class(py_class)

    def test_should_compile_str_str_dict(
        self, class_with_str_str_dict: ClassFixture
    ) -> None:
        ts_model = _compile_py_class(class_with_str_str_dict.py_class)

        assert ts_model == TsModel.of_types([class_with_str_str_dict.ts_object_type])

    def test_should_compile_str_str_default_dict(
        self, class_with_str_str_default_dict: ClassFixture
    ) -> None:
        ts_model = _compile_py_class(class_with_str_str_default_dict.py_class)

        assert ts_model == TsModel.of_types(
            [class_with_str_str_default_dict.ts_object_type]
        )

    def test_should_compile_str_str_ordered_dict(
        self, class_with_str_str_ordered_dict: ClassFixture
    ) -> None:
        ts_model = _compile_py_class(class_with_str_str_ordered_dict.py_class)

        assert ts_model == TsModel.of_types(
            [class_with_str_str_ordered_dict.ts_object_type]
        )


class TestCompileEnum:
    def test_should_compile_int_enum(self, simple_int_enum: EnumFixture) -> None:
        ts_model = _compile_py_enum(simple_int_enum.py_enum)

        assert ts_model == TsModel.of_enums([simple_int_enum.ts_enum])

    def test_should_compile_str_enum(self, simple_str_enum: EnumFixture) -> None:
        ts_model = _compile_py_enum(simple_str_enum.py_enum)

        assert ts_model == TsModel.of_enums([simple_str_enum.ts_enum])

    def test_compile_enum_with_non_str_int_values_should_fail(self) -> None:
        class MyEnum(Enum):
            pass

        py_enum = PyEnum(
            name="test",
            type=MyEnum,
            values=(PyEnumValue(name="test", value=(1,)),),
        )

        with pytest.raises(UnsupportedEnumValue):
            _compile_py_enum(py_enum)


def test_should_convert_casing_to_camel_case(class_with_empty_class):
    model = Model.of_classes([class_with_empty_class.py_class])
    model_compiler = TypescriptModelCompiler(
        TypescriptModelCompilerSettings(field_case_format=CaseFormat.CAMEL_CASE)
    )
    ts_model = model_compiler.compile(model)

    assert ts_model == TsModel.of_types(
        [
            TsObjectType(
                name="ClassWithEmptyClass",
                fields=(TsField(name="emptyClass", type=TsType("EmptyClass")),),
            )
        ]
    )


def test_type_with_override_should_compile_to_overriden_type(
    class_with_empty_class: ClassFixture, empty_class: ClassFixture
) -> None:
    model = Model.of_classes([class_with_empty_class.py_class])
    model_compiler = TypescriptModelCompiler(
        TypescriptModelCompilerSettings(type_mapping_overrides={empty_class.cls: str})
    )
    ts_model = model_compiler.compile(model)

    assert ts_model == TsModel.of_types(
        [
            TsObjectType(
                name="ClassWithEmptyClass",
                fields=(TsField(name="empty_class", type=TS_STRING),),
            )
        ]
    )


class TestCompileTaggedUnion:
    def test_compile_tagged_union_child(
        self, class_with_tagged_union_discriminant_single_child_child
    ):
        model = Model.of_classes(
            [class_with_tagged_union_discriminant_single_child_child.py_class]
        )
        model_compiler = TypescriptModelCompiler(TypescriptModelCompilerSettings())
        ts_model = model_compiler.compile(model)

        assert ts_model == TsModel.of_types(
            [
                TsObjectType(
                    name="ClassWithTaggedUnionDiscriminantSingleChildChild",
                    fields=(),
                    discriminator=TsDiscriminator(name="my_type", value="CHILD"),
                )
            ]
        )

    def test_compile_tagged_union_parent(
        self, class_with_tagged_union_discriminant_single_child
    ):
        model = Model.of_classes(
            [class_with_tagged_union_discriminant_single_child.py_class]
        )
        model_compiler = TypescriptModelCompiler(TypescriptModelCompilerSettings())
        ts_model = model_compiler.compile(model)

        assert ts_model == TsModel.of_types(
            [
                TsUnionType(
                    name="ClassWithTaggedUnionDiscriminantSingleChild",
                    union_members=("ClassWithTaggedUnionDiscriminantSingleChildChild",),
                )
            ]
        )
