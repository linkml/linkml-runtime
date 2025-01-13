import json
from typing import Union, List, Dict, Tuple, Optional, Callable, Any, Iterator
from hbreader import hbread

from .extendednamespace import ExtendedNamespace

# Possible types in the JsonObj representation
JsonObjTypes = Union["JsonObj", List["JsonObjTypes"], str, bool, int, float, None]

# Types in the pure JSON representation
JsonTypes = Union[Dict[str, "JsonTypes"], List["JsonTypes"], str, bool, int, float, None]

# Control variables -- note that subclasses can add to this list
hide = ['_if_missing', '_root']


class JsonObj(ExtendedNamespace):
    """ A namespace/dictionary representation of a JSON object. Any name in a JSON object that is a valid python
    identifier is represented as a first-class member of the objects.  JSON identifiers that begin with "_" are
    disallowed in this implementation.
    """
    # Set this class variable to False if recursive construction is absolutely necessare (see: test_issue13.py for
    # details
    _idempotent = True

    def __new__(cls, *args, _if_missing: Callable[["JsonObj", str], Tuple[bool, Any]] = None, **kwargs):
        """ Construct a JsonObj from set of keyword/value pairs

        :param list_or_dict: A list or dictionary that can be used to construct the object
        :param _if_missing: Function to call if attempt is made to access an undefined value.  Function takes JsonObj
        instance and parameter as input and returns a tuple -- handled (y or n) and result.  If handled is 'n' inline
        processing proceeds.
        :param kwargs: A dictionary as an alternative constructor.
        """
        # This makes JsonObj idempotent
        if cls._idempotent and args and isinstance(args[0], JsonObj):
            # If we're being called with a single argument
            if not kwargs and not args[1:] and\
                    (not _if_missing or _if_missing == args[0]._if_missing) and cls == type(args[0]):
                return args[0]
        obj = super(ExtendedNamespace, cls).__new__(cls)
        return obj

    def __init__(self, *args, _if_missing: Callable[["JsonObj", str], Tuple[bool, Any]] = None, **kwargs):
        """ Construct a JsonObj from set of keyword/value pairs

        :param list_or_dict: A list or dictionary that can be used to construct the object
        :param _if_missing: Function to call if attempt is made to access an undefined value.  Function takes JsonObj
        instance and parameter as input and returns a tuple -- handled (y or n) and result.  If handled is 'n' inline
        processing proceeds.
        :param kwargs: A dictionary as an alternative constructor.
        """
        if args and isinstance(args[0], JsonObj) and not kwargs and not args[1:] and type(self)._idempotent and \
                    (not _if_missing or _if_missing == args[0]._if_missing) and type(self) == type(args[0]):
            return

        if _if_missing and _if_missing != self._if_missing:
            self._if_missing = _if_missing
        if args:
            if kwargs:
                raise TypeError("Constructor can't have both a single item and a dict")
            if isinstance(args[0], JsonObj):
                pass
            elif isinstance(args[0], dict):
                self._init_from_dict(args[0])
            elif isinstance(args[0], list):
                ExtendedNamespace.__init__(self,
                                           _root=[JsonObj(e) if isinstance(e, (dict, list)) else
                                                  e for e in args[0]])
            else:
                raise TypeError("JSON Object can only be a list or dictionary")
        else:
            self._init_from_dict(kwargs)

    @staticmethod
    def _if_missing(obj: "JsonObj", item: str) -> Tuple[bool, Any]:
        return False, None

    def _init_from_dict(self, d: Union[dict, "JsonObj"]) -> None:
        """ Construct a JsonObj from a dictionary or another JsonObj """
        if not isinstance(d, JsonObj):
            ExtendedNamespace.__init__(self, _if_missing=self._if_missing,
                                       **{str(k): JsonObj(v) if isinstance(v, dict) else v for k, v in d.items()})

    def _hide_list(self):
        return self._root if '_root' in self else self

    def __str__(self) -> str:
        return str(self._root) if '_root' in self else super().__str__()

    # ===================================================
    # JSON Serializer method
    # ===================================================
    @staticmethod
    def _static_default(obj, filtr: Callable[[Dict], Dict] = lambda e: e):
        """ return a serialized version of obj or raise a TypeError.  Used by the JSON serializer

        :param obj:
        :param filtr: dictionary filter
        :return: Serialized version of obj
        """
        return filtr(obj._as_dict) if isinstance(obj, JsonObj) else json.JSONDecoder().decode(obj)

    def _default(self, obj, filtr: Callable[[Dict], Dict] = lambda e: e):
        """ This default method is here to allow inheriting classes to override it when needed """
        return JsonObj._static_default(obj, filtr)

    # ===================================================
    # Underscore equivalent of useful dictionary functions
    # ===================================================
    def _get(self, item: str, default: JsonObjTypes = None) -> JsonObjTypes:
        """ Equivalent to dictionary get function w/o polluting namespace """
        return self[item] if item in self else default

    def _setdefault(self, k: str, value: Union[Dict, JsonTypes]) -> JsonObjTypes:
        """ Equivalent of dictionary setdefault without messing in namespace """
        if k not in self:
            self[k] = JsonObj(_if_missing=self._if_missing, **value) if isinstance(value, dict) else value
        return self[k]

    def _keys(self) -> List[str]:
        """ Return all non-hidden keys """
        for k in self._hide_list().__dict__.keys():
            if k not in hide:
                yield k

    def _items(self) -> List[Tuple[str, JsonObjTypes]]:
        """ Return all non-hidden items """
        for k, v in self._hide_list().__dict__.items():
            if k not in hide:
                yield k, v

    def _values(self) -> List[JsonObjTypes]:
        """ Return all non hidden values """
        for _, v in self._items():
            yield v

    # ===================================================
    # Various converters -- use exposed methods in place of underscores
    # ===================================================
    def _as_json_obj(self) -> JsonTypes:
        """ Return self as pure json """
        return json.loads(self._as_json_dumps())

    def __getitem__(self, item):
        if '_root' in self:
            return self._root[item]
        else:
            found, val = self._if_missing(self, item)
            if found:
                return val
            else:
                return super().__getitem__(item)

    def __getattr__(self, item):
        found, val = self._if_missing(self, item)
        if found:
            return val
        else:
            return super().__getattribute__(item)

    def __setattr__(self, key, value):
        super().__setattr__(key, JsonObj(value) if isinstance(value, dict) else value)

    def __bool__(self):
        if '_root' in self:
            return bool(self._root)
        else:
            return bool(any(self._keys()))

    @property
    def _as_json(self) -> str:
        """ Convert a JsonObj into straight json text

        :return: JSON formatted str
        """
        return json.dumps(self, default=self._default)

    def _as_json_dumps(self, indent: str = '   ', filtr: Callable[[Dict], Dict] = None, **kwargs) -> str:
        """ Convert to a stringified json object.

        This is the same as _as_json with the exception that it isn't
        a property, meaning that we can actually pass arguments...
        :param indent: indent argument to dumps
        :param filtr: dictionary filter
        :param kwargs: other arguments for dumps
        :return: JSON formatted string
        """
        return json.dumps(self,
                          default=lambda obj: self._default(obj, filtr) if filtr else self._default(obj),
                          indent=indent,
                          **kwargs)

    @property
    def _as_dict(self) -> Dict[str, JsonTypes]:
        """ Convert a JsonObj into a straight dictionary

        :return: dictionary that cooresponds to the json object
        """
        return as_dict(self)


def loads(s: str, **kwargs) -> JsonObj:
    """ Convert a json_str into a JsonObj

    :param s: a str instance containing a JSON document
    :param kwargs: arguments see: json.load for details
    :return: JsonObj representing the json string
    """
    if isinstance(s, (bytes, bytearray)):
        s = s.decode(json.detect_encoding(s), 'surrogatepass')

    return JsonObj(json.loads(s, object_hook=lambda pairs: JsonObj(pairs), **kwargs))


def load(source, **kwargs) -> JsonObj:
    """ Deserialize a JSON source.

    :param source: a URI, File name or a .read()-supporting file-like object containing a JSON document
    :param kwargs: arguments. see: json.load for details
    :return: JsonObj representing fp
    """
    return loads(hbread(source, accept_header="application/json, text/json;q=0.9"), **kwargs)


def is_dict(obj: Union[JsonObj, Any]) -> bool:
    """
    Determine whether obj is a dictionary or a JsonObj containing a dictionary
    """
    return isinstance(obj, dict) or (isinstance(obj, JsonObj) and not isinstance(obj._hide_list(), list))


def is_list(obj: Union[JsonObj, Any]) -> bool:
    """
    Determine whether obj is a dictionary or a JsonObj containing a dictionary
    """
    return isinstance(obj, list) or (isinstance(obj, JsonObj) and isinstance(obj._hide_list(), list))


def as_dict(obj: Union[JsonObj, List]) -> Union[List, Dict[str, JsonTypes]]:
    """ Convert a JsonObj into a straight dictionary or list

    :param obj: pseudo 'self'
    :return: dictionary that cooresponds to the json object
    """
    if isinstance(obj, (list, JsonObj)):
        return \
            {k: as_dict(v) if isinstance(v, (list, dict, JsonObj)) else v
             for k, v in items(obj)} if is_dict(obj) else \
            [as_dict(e) if isinstance(e, (list, dict, JsonObj)) else
             e for e in (obj._hide_list() if isinstance(obj, JsonObj) else obj)]
    else:
        return obj

def as_json(obj: Union[Dict, JsonObj, List], indent: Optional[str] = '   ',
            filtr: Callable[[Dict], Dict] = None, **kwargs) -> str:
    """ Convert obj to json string representation.

        :param obj: pseudo 'self'
        :param indent: indent argument to dumps
        :param filtr: filter to remove unwanted elements
        :param kwargs: other arguments for dumps
        :return: JSON formatted string
       """
    if isinstance(obj, JsonObj) and '_root' in obj:
        obj = obj._root
    default_processor = \
        obj._default if isinstance(obj, JsonObj) else JsonObj._static_default
    return obj._as_json_dumps(indent,
                              filtr=filtr,
                              **kwargs) if isinstance(obj, JsonObj) else \
        json.dumps(obj,
                   default=lambda o: default_processor(o, filtr) if filtr else default_processor(o),
                   indent=indent,
                   *kwargs)


def as_json_obj(obj: Union[Dict, JsonObj, List]) -> JsonTypes:
    """ Return obj as pure python json (vs. JsonObj)
        :param obj: pseudo 'self'
        :return: Pure python json image
    """
    if isinstance(obj, JsonObj):
        obj = obj._hide_list()
    return [as_json_obj(e) for e in obj] if isinstance(obj, list) else\
        obj._as_json_obj() if isinstance(obj, JsonObj) else obj


def get(obj: Union[Dict, JsonObj], item: str, default: JsonObjTypes = None) -> JsonObjTypes:
    """ Dictionary get routine """
    return obj._get(item, default) if isinstance(obj, JsonObj) else obj.get(item, default)


def setdefault(obj: Union[Dict, JsonObj], k: str, value: Union[Dict, JsonTypes]) -> JsonObjTypes:
    """ Dictionary setdefault routine """
    return obj._setdefault(k, value) if isinstance(obj, JsonObj) else obj.setdefault(k, value)


def keys(obj: Union[Dict, JsonObj]) -> Iterator[str]:
    """ same as dict keys() without polluting the namespace """
    return obj._keys() if isinstance(obj, JsonObj) else obj.keys()


def items(obj: Union[Dict, JsonObj]) -> Iterator[Tuple[str, JsonObjTypes]]:
    """ Same as dict items() except that the values are JsonObjs instead of vanilla dictionaries
    :return:
    """
    return obj._items() if isinstance(obj, JsonObj) else obj.items()


def values(obj: Union[Dict, JsonObj]) -> Iterator[JsonObjTypes]:
    """ Same as dict values() except that the values are JsonObjs """
    return obj._values() if isinstance(obj, JsonObj) else obj.values()
