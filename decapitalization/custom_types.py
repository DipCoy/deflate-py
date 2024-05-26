from typing import TypeVar, Generator, Any


DeviationsPositions = TypeVar('DeviationsPositions', bound=list[int])
DecapitalizedText = TypeVar('DecapitalizedText', bound=str)
Symbol = TypeVar('Symbol', bound=str)
TextReader = TypeVar('TextReader', bound=Generator[str, Any, None])
