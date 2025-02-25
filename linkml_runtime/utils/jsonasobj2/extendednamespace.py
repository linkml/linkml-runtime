

class ExtendedNamespace:
    """ A combination of a namespace and a dictionary.  This allows direct access to python properties plus
    dictionary access to everything.
    """
    def __init__(self, **kwargs):
        for name in kwargs:
            setattr(self, name, kwargs[name])

    def __eq__(self, other):
        if not isinstance(other, ExtendedNamespace):
            return NotImplemented
        return vars(self) == vars(other)

    def __contains__(self, key):
        return key in self.__dict__

    def __getitem__(self, item):
        return self.__dict__[item]

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return self.__dict__.__iter__()

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        star_args = {}
        for name, value in list(self.__dict__.items()):
            if not name.startswith('_'):
                if name.isidentifier():
                    arg_strings.append('%s=%r' % (name, value))
                else:
                    star_args[name] = value
        if star_args:
            arg_strings.append('**%s' % repr(star_args))
        return '%s(%s)' % (type_name, ', '.join(arg_strings))

    def _get(self, key, default=None):
        return self.__dict__.get(key, default)
