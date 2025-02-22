[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
# py2ts-generator

> [!NOTE]
> This package was originally forked from [Latios96/py-typescript-generator](https://github.com/Latios96/py-typescript-generator) in order to add support for SQLAlchemy 2 models.

`py2ts-generator` is a tool to create TypeScript type definitions from Python classes. 

> [!NOTE]
>  Currently, Python dataclasses and basic SQLAlchemy models are supported, but it's possible to extend this to other sources. For more details, see [Adding Parsers](#adding-parsers).

This project is heavily inspired by the [typescript-generator](https://github.com/vojtechhabarta/typescript-generator) project by 
Vojtěch Habarta, a TypeScript generator for Java classes.

**Example**  
Consider the following dataclass:
```python
from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class DemoClass:
    my_int: int
    my_optional_string: Optional[str]
    my_list: List[str]
    my_dict: Dict[str, str]
```
For this class, the following TypeScript interface is generated:
```typescript
interface DemoClass {
    my_int: number
    my_optional_string: string | undefined
    my_list: string[]
    my_dict: { [index: string]: string }
}
```
`py2ts-generator` supports basic Python types like `int`, `float`, `str`, `datetime` or `UUID` and collections like `List`, `Set` or `Dict`. `Optional` is also supported.

For more details on type mapping, see [Type Mapping](#type-mapping).

## Usage
### Installation
You can install `py2ts-generator` via `pip`, currently only from Github:
```shell
pip install git+https://github.com/EnlitHamster/py2ts-generator.git@0.1.0
```
or if you are using poetry:
```shell
poetry add git+ssh://git@github.com:EnlitHamster/py2ts-generator.git#0.1.0
```
### Invocation
`py2ts-generator` is invoked by a custom Python Script, which is placed in your project. Note that `py2ts-generator` needs to import your classes, so make sure all your imported dependencies are available when generating your types.

To generate your TypeScript types, pass a list of your classes: 

```python
from dataclasses import dataclass
from py2ts_generator import TypeGenerationPipelineBuilder

@dataclass
class MyExampleClass:
    value: int

if __name__ == "__main__":
    TypeGenerationPipelineBuilder() \
        .for_types([MyExampleClass]) \ 
        .to_file("demo.ts") \
        .build() \
        .run()
```
Types used as field types are automatically discovered and don't have to be passed in manually.

Now just execute the script you created and your TypeScript types are generated to the file path you configured.

### Advanced features
#### Type overrides
You can override how a certain type is mapped in TypeScript. This is usefull if a type is represented diffenent in JSON as in your Python dataclass. For example, a `datetime` object by default is mapped to a `string`, but you might return them in JSON as UNIX timestamps. In this case, you override the `datetime` mapping to `int`:  
```python
TypeGenerationPipelineBuilder() \
    .for_types([MyExampleClass]) \ 
    .with_type_overrides({datetime: int})
    .to_file("demo.ts") \
    .build() \
    .run()
```
#### CamelCase conversion
In Python, fields are usually declared in snake_case. However, sometimes they are converted to camelCase in JSON, since this is the convention in JavaScript / TypeScript. `py2ts-generator` also supports camelCase conversion for fields:
```python
TypeGenerationPipelineBuilder() \
    .for_types([MyExampleClass]) \ 
    .convert_field_names_to_camel_case()
    .to_file("demo.ts") \
    .build() \
    .run()
```


## Type Mapping
Python classes and Enums are supported. Python classes are mapped as TypeScript interfaces, Enums are mapped as TypeScript enums.
> Note: only str and int values are supported for Enums.

Currently, only Python dataclasses can be analyzed and mapped. However, this can be extended.

The following Python types are automatically recognized and mapped as following:

| Python type         | Typescript type                                        |
|---------------------|--------------------------------------------------------|
| int                 | number                                                 |
| float               | number                                                 |
| str                 | str                                                    |
| bytes               | str                                                    |
| bool                | boolean                                                |
| datetime            | str                                                    |
| UUID                | str                                                    |
| Optional[T]         | T \| undefined         |
| List[T]             | T[]                                                    |
| Set[T]              | T[]                     |
| FrozenSet[T]        | T[]                     |
| OrderedSet[T]       | T[]                     |
| Dict[str, T]        | { [index: string]: T } (Fails, if key type is not str) |
| DefaultDict[str, T] | { [index: string]: T } (Fails, if key type is not str) |

## Adding Parsers

Another customization option is to add class parsers for the model parser to use. To start, you need to override the `AbstractClassParser` class. The example shows how you can create a parser for classes extending your base model. We will assume that the base model provides a `get_ts_attrs` method that provides a `dict[str, Type]` mapping to be used to generate a `PyClass` object.

```python
from py2ts_generator.model.py_class import PyClass
from py2ts_generator.model.py_field import PyField
from py2ts_generator.model_parser.class_parsers.abstract_class_parser import AbstractClassParser

from my_package import MyCustomBaseClass

from typing_extensions import override


class NotMyClassError(Exception):
    def __init__(self, cls: Type, *args, **kwargs) -> None:
        super().__init__(f'Not my class: {cls.__name__}', *args, **kwargs)


class MyCustomClassParser(AbstractClassParser):
    @override
    def accepts_class(self, cls: Type) -> bool:
        return isinstance(cls, MyCustomBaseClass)

    @override
    def parse(self, cls: Type) -> PyClass:
        if not self.accepts_class(cls):
            raise NotMyClassError(cls)

        fields = [
            PyField(name=name, type=type)
            for name, typ in cls.get_ts_attrs().items()
        ]

        return PyClass(name=cls.__name__, type=cls, fields=tuple(fields))

```

Then, when building your pipeline:

```python
from py2ts_generator import TypeGenerationPipelineBuilder

from my_package import MyCustomClassParser


if __name__ == "__main__":
    TypeGenerationPipelineBuilder() \
        .for_types([MyExampleClass]) \ 
        .with_parsers([MyCustomClassParser()]) \
        .to_file("demo.ts") \
        .build() \
        .run()
```
