def print_before_and_after(**identifiers):
    def wrapper(func):
        def f(*args, **kwargs):
            print(f"Before function {func.__name__}:")
            for i in identifiers:
                print(i)
            ret = func(*args, **kwargs)
            print(f"After function {func.__name__}:")
            for i in identifiers:
                print(i)
            return ret

        return f

    return wrapper
