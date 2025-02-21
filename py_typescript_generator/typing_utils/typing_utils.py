from typing import Type, Optional, TypeVar

from typing_inspect import get_args  # type: ignore

T = TypeVar("T")


class UnknownTypeError(Exception):
    def __init__(self, type_name: str, *args: object, **kwargs: dict) -> None:
        """ Exception raised if a type could not be found from a type name.

        :param type_name: The type name.
        """
        super().__init__(f'Unknown type "{type_name}"', *args, **kwargs)


def get_wrapped_type_from_optional(cls: Type) -> Type:
    args = get_args(cls)
    return args[0]  # type: ignore


def safe_unwrap(optional: Optional[T]) -> T:
    if optional is None:
        raise ValueError("Tried to unwrap an optional, but it was None.")
    return optional


def get_type(type_name: str) -> Optional[Type]:
    """ Attempts to get the type from its name.

    :param type_name: The type name.

    :returns: The found type.

    :raises UnknownTypeError: If the type name could not be found in
        either builtins or globals.
    """
    import builtins

    try:
        return getattr(builtins, type_name)  # type: ignore
    except AttributeError:
        try:
            obj = globals()[type_name]
        except KeyError:
            raise UnknownTypeError(type_name)
        return obj if isinstance(obj, type) else None  # type: ignore
