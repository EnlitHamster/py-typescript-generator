import os
from pathlib import Path
from typing import List, Optional, Type, Dict, Union

from py2ts_generator.model.model import Model
from py2ts_generator.model_parser.class_parsers.abstract_class_parser import (
    AbstractClassParser,
)
from py2ts_generator.model_parser.class_parsers.dataclass_parser import (
    DataclassParser,
)
from py2ts_generator.model_parser.class_parsers.sqlalchemy_parser import (
    SQLAlchemyParser,
)
from py2ts_generator.model_parser.model_parser import (
    ModelParser,
    ModelParserSettings,
)
from py2ts_generator.typescript_emitter.typescript_emitter import (
    TypescriptEmitter,
)
from py2ts_generator.typescript_model_compiler.ts_model import TsModel
from py2ts_generator.typescript_model_compiler.typescript_model_compiler import (
    CaseFormat,
    TypescriptModelCompiler,
    TypescriptModelCompilerSettings,
)


class TypeGenerationPipeline:
    def __init__(
        self,
        types: List[Type],
        type_overrides: Dict[Type, Type],
        case_format: CaseFormat,
        output_file: Union[str, Path],
        class_parsers: Optional[List[AbstractClassParser]] = None,
    ):
        self.types = types
        self.type_overrides = type_overrides
        self.case_format = case_format
        self.output_file = output_file
        self.class_parsers = class_parsers or [DataclassParser(), SQLAlchemyParser()]

    def run(self) -> None:
        model = self._parse_model()
        ts_model = self._compile_model(model)
        emitted_model = self._emit_model(ts_model)
        self._write_model(emitted_model)

    def _parse_model(self) -> Model:
        model_parser = ModelParser(
            self.types,
            self.class_parsers,
            ModelParserSettings(type_mapping_overrides=self.type_overrides),
        )
        model = model_parser.parse()
        return model

    def _compile_model(self, model: Model) -> TsModel:
        ts_model = TypescriptModelCompiler(
            TypescriptModelCompilerSettings(
                field_case_format=self.case_format,
                type_mapping_overrides=self.type_overrides,
            )
        ).compile(model)
        return ts_model

    def _emit_model(self, ts_model: TsModel) -> str:
        emitted_model = TypescriptEmitter().emit(ts_model)
        return emitted_model

    def _write_model(self, emitted_model: str) -> None:
        self._create_target_folder_if_not_exists()
        with open(self.output_file, "w") as f:
            f.write(emitted_model)

    def _create_target_folder_if_not_exists(self):
        folder = os.path.dirname(self.output_file)
        if not os.path.exists(folder):
            os.makedirs(folder)
