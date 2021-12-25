from sys import version_info

if version_info >= (3, 9):
    Set = set
    List = list
    Dict = dict
    Tuple = tuple
    from typing import Any, Optional, Callable
else:
    from typing import Set, Dict, List, Tuple, Callable, Any, Optional
