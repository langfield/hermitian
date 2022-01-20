import re
import sys
import contextlib
import collections

# pylint: disable=unused-import

if sys.version_info >= (3, 9):
    Tuple = tuple
    List = list
    Dict = dict
    Set = set
    FrozenSet = frozenset
    Type = type

    Deque = collections.deque
    DefaultDict = collections.defaultdict
    OrderedDict = collections.OrderedDict
    Counter = collections.Counter
    ChainMap = collections.ChainMap

    Awaitable = collections.abc.Awaitable
    Coroutine = collections.abc.Coroutine
    AsyncIterable = collections.abc.AsyncIterable
    AsyncIterator = collections.abc.AsyncIterator
    AsyncGenerator = collections.abc.AsyncGenerator
    Iterable = collections.abc.Iterable
    Iterator = collections.abc.Iterator
    Generator = collections.abc.Generator
    Reversible = collections.abc.Reversible
    Container = collections.abc.Container
    Collection = collections.abc.Collection
    Callable = collections.abc.Callable
    MutableSet = collections.abc.MutableSet
    Mapping = collections.abc.Mapping
    MutableMapping = collections.abc.MutableMapping
    Sequence = collections.abc.Sequence
    MutableSequence = collections.abc.MutableSequence
    ByteString = collections.abc.ByteString
    MappingView = collections.abc.MappingView
    KeysView = collections.abc.KeysView
    ItemsView = collections.abc.ItemsView
    ValuesView = collections.abc.ValuesView

    ContextManager = contextlib.AbstractContextManager
    AsyncContextManager = (
        contextlib.AbstractAsyncContextManager
    )  # typing.AsyncContextManager
    Pattern = re.Pattern  # typing.Pattern, typing.re.Pattern
    Match = re.Match  # typing.Match, typing.re.Match

    from typing import Any, Optional, Annotated, Union
else:
    from typing import Set, Dict, List, Tuple, FrozenSet, Type, Any, Optional, Union
    from typing import (
        AbstractSet,
        Deque,
        DefaultDict,
        OrderedDict,
        Counter,
        ChainMap,
        Awaitable,
        Coroutine,
        AsyncIterable,
        AsyncIterator,
        AsyncGenerator,
        Iterable,
        Iterator,
        Generator,
        Reversible,
        Container,
        Collection,
        Callable,
        MutableSet,
        Mapping,
        MutableMapping,
        Sequence,
        MutableSequence,
        ByteString,
        MappingView,
        KeysView,
        ItemsView,
        ValuesView,
    )
    from typing import AsyncContextManager
    from typing.re import Pattern, Match
    from typing_extensions import Annotated
