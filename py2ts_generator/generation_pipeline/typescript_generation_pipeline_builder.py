from pathlib import Path
from typing import List, Self, Type, Dict, Optional

from py2ts_generator.generation_pipeline.typescript_generation_pipeline import (
    TypeGenerationPipeline,
)
from py2ts_generator.model_parser.class_parsers.abstract_class_parser import (
    AbstractClassParser,
)
from py2ts_generator.typescript_model_compiler.typescript_model_compiler import (
    CaseFormat,
)


class NoOutputFileDefined(Exception):
    def __init__(self):
        super(NoOutputFileDefined, self).__init__(
            "No output file was defined, please use to_file() to provide an output file."
        )


class TypeGenerationPipelineBuilder:
    def __init__(self) -> None:
        self._types: List[Type] = []
        self._type_overrides: Dict[Type, Type] = {}
        self._case_format: CaseFormat = CaseFormat.KEEP_CASING
        self._output_file: Optional[str | Path] = None
        self._class_parsers: Optional[List[AbstractClassParser]] = None

    def for_types(self, types: List[Type]) -> 'TypeGenerationPipelineBuilder':
        self._types = types
        return self

    def with_type_overrides(self, type_overrides: Dict[Type, Type]) -> 'TypeGenerationPipelineBuilder':
        self._type_overrides = type_overrides
        return self

    def convert_field_names_to_camel_case(self) -> 'TypeGenerationPipelineBuilder':
        self._case_format = CaseFormat.CAMEL_CASE
        return self

    def to_file(self, path: str | Path) -> 'TypeGenerationPipelineBuilder':
        self._output_file = path
        return self

    def with_parsers(self, parsers: List[AbstractClassParser]) -> 'TypeGenerationPipelineBuilder':
        self._class_parsers = parsers
        return self

    def build(self) -> TypeGenerationPipeline:
        if not self._output_file:
            raise NoOutputFileDefined()
        return TypeGenerationPipeline(
            self._types,
            self._type_overrides,
            self._case_format,
            self._output_file,
            self._class_parsers,
        )
