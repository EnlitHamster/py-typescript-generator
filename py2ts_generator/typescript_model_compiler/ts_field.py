from dataclasses import dataclass

from py2ts_generator.typescript_model_compiler.ts_type import TsType


@dataclass(frozen=True)
class TsField:
    name: str
    type: TsType
