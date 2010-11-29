import functools
import types

def map_ind(funcs, iterable, fallback = None):
    """
    Map function to item individually.
    
    The fallback parameter is used, when an item has
    no corresponding function.
    
    """
    result = []
    for i, value in enumerate(iterable):
        f = None
        f = funcs[i] if i < len(funcs) else fallback
        if callable(f):
            value = f(value)
        result.append(value)
    return result

def partial(func, *args, **kwargs):
    prt = functools.partial
    partial_ = prt(func, *args, **kwargs)
    partial_.partial = prt(prt, partial_)
    return partial_

def hook_args(func, hooks, fallback = None):
    """Apply specific hooks to positional arguments."""
    @functools.wraps(func)
    def hooked(*args, **kwargs):
        args = map_ind(hooks, args, fallback)
        return func(*args, **kwargs)
    return hooked

def hooks_kwargs(wrapped, hooks, fallback = None):
    """Apply specific hooks to named arguments."""
    # Gather variable names
    if isinstance(wrapped, types.MethodType):
        # We don't want the self parameter really...
        var_names = wrapped.im_func.func_code.co_varnames
    else:
        var_names = wrapped.func_code.co_varnames

    # Build lookup table key -> func
    # Transform func -> (key1, key2) into key1 -> func, key2 -> func
    key_func = dict()
    for key, value in hooks.iteritems():
        if isinstance(key, str):
            if not callable(value):
                raise ValueError("Uncallable object provided: %s" % value)
            if key in key_func:
                    raise ValueError("Duplicate key: %s" % key)
            key_func[key] = value
        elif callable(key):
            func, keys = (key, value)
            for key in keys:
                if key in key_func:
                    raise ValueError("Duplicate key: %s" % key)
                key_func[key] = func
        else:
            raise ValueError("Uncallable object provided: %s" % value)

    # Build args hook
    hooks = []
    print var_names
    for key in var_names:
        hooks.append(key_func[key] if key in key_func else None)
    print key_func
    print hooks
    def hooked(*args, **kwargs):
        args = map_ind(hooks, args)
        processed = kwargs.copy()
        for key, func in key_func.iteritems():
            if key in processed:
                processed[key] = func(processed[key])
        return wrapped(*args, **processed)
    return hooked

def chain(outer, inner, *args):
    """
    Chain functions
    
    The order in which the functions, in which
    they are passed to the functions, matches
    the way you write them down, if you chain
    them directly.
    
    If you were to do:
        a(b(c(*args, **kwargs)))
    You would call:
        chained(a, b, c)
    
    """
    functions = list(args)
    functions.reverse()
    functions.extend([inner, outer])
    def chained(*args, **kwargs):
        # Call first functions with original arguments
        result = functions[0](*args, **kwargs)
        for func in functions[1:]:
            result = func(result)
        return result
    return chained

def iterate(func, times = 2):
    """Iterate a functions over it's own result."""
    def iterated(arg):
        result = arg
        for i in range(0, times):
            result = func(result)
        return result
    return iterated


def merge():
    """
    Merge functions
    
    merge(func, a, b) -> lambda: func(a(), b()) 
    """

