def hello_world():
    return "Hello World, This is easyprophet pack."


def capital_case(x):
    if not isinstance(x, str):
        raise TypeError("Please provide a string argument")
    return x.capitalize()