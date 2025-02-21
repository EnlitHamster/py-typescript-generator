from datetime import datetime
from typing import (
    Type,
    List,
    Set,
    Dict,
    Tuple,
    Union,
    FrozenSet,
    DefaultDict,
)
from uuid import UUID

import pytest
from ordered_set import OrderedSet

from py2ts_generator.model.model import Model
from py2ts_generator.model.py_class import PyClass
from py2ts_generator.model.py_field import PyField
from py2ts_generator.model_parser.class_parsers.abstract_class_parser import (
    AbstractClassParser,
)
from py2ts_generator.model_parser.model_parser import (
    ModelParser,
    NoParserForClassFoundException,
    IsNotAClassException,
    ModelParserSettings,
)
from tests.unittests.demo_parser_fixture import DemoParser
from tests.unittests.fixture_classes import (
    ClassFixture,
    EnumFixture,
    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_SINGLE_CHILD_CHILD,
    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_SINGLE_CHILD,
    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_MULTIPLE_CHILDREN,
    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_MULTIPLE_CHILDREN_CHILD_1,
    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_MULTIPLE_CHILDREN_CHILD_2,
    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_ENUM_DISCRIMINATOR_CHILD,
)


def test_should_raise_exception_if_no_parser_for_class_was_found(demo_parser):
    class UnknownClass:
        pass

    model_parser = ModelParser([UnknownClass], [demo_parser], ModelParserSettings())

    with pytest.raises(NoParserForClassFoundException):
        model_parser.parse()


def test_should_raise_exception_if_passed_thing_is_not_a_class(demo_parser):
    model_parser = ModelParser([lambda x: x], [demo_parser], ModelParserSettings())

    with pytest.raises(IsNotAClassException):
        model_parser.parse()


class TestParseSimpleClass:
    def test_model_should_contain_just_the_simple_class(
        self, empty_class: ClassFixture, demo_parser: DemoParser
    ) -> None:
        model_parser = ModelParser(
            [empty_class.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()

        assert model == Model(classes=OrderedSet([empty_class.py_class]))

    def test_model_should_contain_just_the_simple_class_even_if_supplied_two_timed(
        self, empty_class: ClassFixture, demo_parser: DemoParser
    ) -> None:
        model_parser = ModelParser(
            [empty_class.cls, empty_class.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()

        assert model == Model(classes=OrderedSet([empty_class.py_class]))


class TestParseClassWithSimpleClass:
    def test_model_should_contain_both_classes_when_passing_only_with_simple_class(
        self,
        empty_class: ClassFixture,
        class_with_empty_class: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_empty_class.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()

        assert model == Model(
            classes=OrderedSet(
                [
                    class_with_empty_class.py_class,
                    empty_class.py_class,
                ]
            )
        )

    def test_model_should_contain_both_classes_when_passing_both_classes(
        self,
        empty_class: ClassFixture,
        class_with_empty_class: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_empty_class.cls, empty_class.cls],
            [demo_parser],
            ModelParserSettings(),
        )

        model = model_parser.parse()

        assert model == Model(
            classes=OrderedSet(
                [
                    class_with_empty_class.py_class,
                    empty_class.py_class,
                ]
            )
        )


class TestClassWithClassWithEmptyClass:
    def test_should_parse_through_three_levels(
        self,
        empty_class: ClassFixture,
        class_with_empty_class: ClassFixture,
        class_with_class_with_empty_class: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_class_with_empty_class.cls],
            [demo_parser],
            ModelParserSettings(),
        )

        model = model_parser.parse()
        assert model == Model(
            classes=OrderedSet(
                [
                    class_with_class_with_empty_class.py_class,
                    class_with_empty_class.py_class,
                    empty_class.py_class,
                ]
            )
        )


class TestParsingCycleShouldTerminate:
    def test_parse_only_first_class_in_cycle(
        self,
        first_class_in_cycle: ClassFixture,
        second_class_in_cycle: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [first_class_in_cycle.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()
        assert model == Model(
            classes=OrderedSet(
                [first_class_in_cycle.py_class, second_class_in_cycle.py_class]
            )
        )

    def test_parse_only_second_class_in_cycle(
        self,
        first_class_in_cycle: ClassFixture,
        second_class_in_cycle: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [second_class_in_cycle.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()
        assert model == Model(
            classes=OrderedSet(
                [
                    second_class_in_cycle.py_class,
                    first_class_in_cycle.py_class,
                ]
            )
        )

    def test_parse_all_in_cycle(
        self,
        first_class_in_cycle: ClassFixture,
        second_class_in_cycle: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [first_class_in_cycle.cls, second_class_in_cycle.cls],
            [demo_parser],
            ModelParserSettings(),
        )

        model = model_parser.parse()
        assert model == Model(
            classes=OrderedSet(
                [first_class_in_cycle.py_class, second_class_in_cycle.py_class]
            )
        )


@pytest.mark.parametrize(
    "the_type",
    [
        int,
        float,
        complex,
        str,
        bytes,
        bool,
        datetime,
        UUID,
        List[int],
        Set[int],
        Dict[str, str],
        Tuple[int],
        Union[str, int],
        FrozenSet[int],
        DefaultDict[str, str],
    ],
)
def test_parse_builtin_terminating_types(
    the_type: Type, class_with_int: ClassFixture
) -> None:
    py_class_with_terminating_type = PyClass(
        name="ClassWithTerminatingType",
        type=class_with_int.cls,
        fields=(PyField(name="the_type", type=the_type),),
    )

    class TerminatingTypeClassParser(AbstractClassParser):
        def accepts_class(self, cls: Type) -> bool:
            return True

        def parse(self, cls: Type) -> PyClass:
            return py_class_with_terminating_type

    model_parser = ModelParser(
        [class_with_int.cls], [TerminatingTypeClassParser()], ModelParserSettings()
    )

    model = model_parser.parse()

    assert model == Model(classes=OrderedSet([py_class_with_terminating_type]))


class TestParseGenericTypes:
    def test_parse_class_with_string_list(
        self, class_with_str_list: ClassFixture, demo_parser: DemoParser
    ) -> None:
        model_parser = ModelParser(
            [class_with_str_list.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()
        assert model == Model(
            classes=OrderedSet(
                [
                    class_with_str_list.py_class,
                ]
            )
        )

    def test_parse_class_with_str_str_dict(
        self, class_with_str_str_dict: ClassFixture, demo_parser: DemoParser
    ) -> None:
        model_parser = ModelParser(
            [class_with_str_str_dict.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()
        assert model == Model(
            classes=OrderedSet(
                [
                    class_with_str_str_dict.py_class,
                ]
            )
        )

    def test_parse_class_with_empty_class_list(
        self,
        empty_class: ClassFixture,
        class_with_empty_class_list: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_empty_class_list.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()
        assert model == Model(
            classes=OrderedSet(
                [
                    class_with_empty_class_list.py_class,
                    empty_class.py_class,
                ]
            )
        )

    def test_should_parse_generic_class_with_type_var(
        self, class_with_generic_member: ClassFixture, demo_parser: DemoParser
    ) -> None:
        model_parser = ModelParser(
            [class_with_generic_member.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()
        assert model == Model(classes=OrderedSet([class_with_generic_member.py_class]))

    def test_should_parse_deeply_nested_generics(
        self,
        empty_class: ClassFixture,
        class_with_deep_nested_generics: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_deep_nested_generics.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()
        assert model == Model(
            classes=OrderedSet(
                [
                    class_with_deep_nested_generics.py_class,
                    empty_class.py_class,
                ]
            )
        )


class TestParseOptional:
    def test_should_parse_optional_int(
        self, class_with_optional_int: ClassFixture, demo_parser: DemoParser
    ) -> None:
        model_parser = ModelParser(
            [class_with_optional_int.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()

        assert model == Model(classes=OrderedSet([class_with_optional_int.py_class]))

    def test_should_also_parse_empty_class(
        self,
        class_with_optional_empty_class: ClassFixture,
        empty_class: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_optional_empty_class.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()

        assert model == Model(
            classes=OrderedSet(
                [class_with_optional_empty_class.py_class, empty_class.py_class]
            )
        )


class TestParseEnums:
    def test_should_parse_simple_int_enum(
        self, simple_int_enum: EnumFixture, demo_parser: DemoParser
    ) -> None:
        model_parser = ModelParser(
            [simple_int_enum.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()

        assert model == Model(enums=OrderedSet([simple_int_enum.py_enum]))

    def test_should_parse_simple_str_enum(
        self, simple_str_enum: EnumFixture, demo_parser: DemoParser
    ) -> None:
        model_parser = ModelParser(
            [simple_str_enum.cls], [demo_parser], ModelParserSettings()
        )

        model = model_parser.parse()

        assert model == Model(enums=OrderedSet([simple_str_enum.py_enum]))


def test_type_with_override_should_not_analyse_original_type(
    class_with_empty_class: ClassFixture,
    empty_class: ClassFixture,
    demo_parser: DemoParser,
) -> None:
    model_parser = ModelParser(
        [class_with_empty_class.cls],
        [demo_parser],
        ModelParserSettings(type_mapping_overrides={empty_class.cls: str}),
    )

    model = model_parser.parse()

    assert model == Model(classes=OrderedSet([class_with_empty_class.py_class]))


class TestParseDiscriminantUnionClasses:
    def test_parse_class_without_children(
        self,
        class_with_tagged_union_discriminant_but_no_children: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_tagged_union_discriminant_but_no_children.cls],
            [demo_parser],
            ModelParserSettings(),
        )

        model = model_parser.parse()

        assert model == Model(
            classes=OrderedSet(
                [class_with_tagged_union_discriminant_but_no_children.py_class]
            )
        )

    def test_parse_root_no_discriminant_value(
        self,
        class_with_tagged_union_discriminant_no_discriminant_for_root: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_tagged_union_discriminant_no_discriminant_for_root.cls],
            [demo_parser],
            ModelParserSettings(),
        )

        model = model_parser.parse()

        assert model == Model(
            classes=OrderedSet(
                [class_with_tagged_union_discriminant_no_discriminant_for_root.py_class]
            )
        )

    def test_parse_enum_discriminant(
        self,
        class_with_tagged_union_discriminant_enum_discriminant: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_tagged_union_discriminant_enum_discriminant.cls],
            [demo_parser],
            ModelParserSettings(),
        )

        model = model_parser.parse()

        assert model == Model(
            classes=OrderedSet(
                [
                    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_ENUM_DISCRIMINATOR_CHILD,
                    class_with_tagged_union_discriminant_enum_discriminant.py_class,
                ]
            )
        )

    def test_parse_class_with_single_child_parse_parent(
        self,
        class_with_tagged_union_discriminant_single_child: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_tagged_union_discriminant_single_child.cls],
            [demo_parser],
            ModelParserSettings(),
        )

        model = model_parser.parse()

        assert model == Model(
            classes=OrderedSet(
                [
                    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_SINGLE_CHILD_CHILD,
                    class_with_tagged_union_discriminant_single_child.py_class,
                ]
            )
        )

    def test_parse_class_with_single_child_parse_child(
        self,
        class_with_tagged_union_discriminant_single_child_child: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_tagged_union_discriminant_single_child_child.cls],
            [demo_parser],
            ModelParserSettings(),
        )

        model = model_parser.parse()

        assert model == Model(
            classes=OrderedSet(
                [
                    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_SINGLE_CHILD,
                    class_with_tagged_union_discriminant_single_child_child.py_class,
                ]
            )
        )

    def test_parse_class_with_multiple_children_parse_parent(
        self,
        class_with_tagged_union_discriminant_multiple_children: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_tagged_union_discriminant_multiple_children.cls],
            [demo_parser],
            ModelParserSettings(),
        )

        model = model_parser.parse()

        assert model == Model(
            classes=OrderedSet(
                [
                    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_MULTIPLE_CHILDREN_CHILD_1,
                    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_MULTIPLE_CHILDREN_CHILD_2,
                    class_with_tagged_union_discriminant_multiple_children.py_class,
                ]
            )
        )

    def test_parse_class_with_multiple_children_parse_child_1(
        self,
        class_with_tagged_union_discriminant_multiple_children_child_1: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_tagged_union_discriminant_multiple_children_child_1.cls],
            [demo_parser],
            ModelParserSettings(),
        )

        model = model_parser.parse()

        assert model == Model(
            classes=OrderedSet(
                [
                    class_with_tagged_union_discriminant_multiple_children_child_1.py_class,
                    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_MULTIPLE_CHILDREN_CHILD_2,
                    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_MULTIPLE_CHILDREN,
                ]
            )
        )

    def test_parse_class_with_multiple_children_parse_child_2(
        self,
        class_with_tagged_union_discriminant_multiple_children_child_2: ClassFixture,
        demo_parser: DemoParser,
    ) -> None:
        model_parser = ModelParser(
            [class_with_tagged_union_discriminant_multiple_children_child_2.cls],
            [demo_parser],
            ModelParserSettings(),
        )

        model = model_parser.parse()

        assert model == Model(
            classes=OrderedSet(
                [
                    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_MULTIPLE_CHILDREN_CHILD_1,
                    class_with_tagged_union_discriminant_multiple_children_child_2.py_class,
                    PY_CLASS_FOR_CLASS_WITH_TAGGED_UNION_DISCRIMINANT_MULTIPLE_CHILDREN,
                ]
            )
        )
