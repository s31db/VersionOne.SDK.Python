def key_by_args_and_func_kw(old_f, args, kw, cache_data):
    """Function to produce a key hash for the cache_data hash based on the function and the arguments
    provided."""
    return repr((old_f, args, kw))


def memoized(old_f):
    """Decorator that memoizes calls to old_f into a single instance-specific _memoized_data hash"""

    def new_f(self, *args, **kw):
        """Function to wrap the decorated method"""
        if not self._memoized_data:
            self._memoized_data = {}
        # generate a hash using the provided hashing function from the closure
        new_key = key_by_args_and_func_kw(old_f, args, kw, self._memoized_data)
        # check if it's already in the memoized data
        if new_key in self._memoized_data:
            # return what's already there
            return self._memoized_data[new_key]
        # not found, call the real function and put the results in the memoized data
        new_value = old_f(self, *args, **kw)
        self._memoized_data[new_key] = new_value
        return new_value

    return new_f


# memoized = cached_by_keyfunc()
