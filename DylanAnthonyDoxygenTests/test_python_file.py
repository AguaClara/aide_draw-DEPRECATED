def run(a,b):
    """
    This function has two floats which belong to [-100,100]

    Args:
        a: float number
        b: float number

    Returns:
        A float number is the result.

    Raises:
        AssertionError, ValueError.

    Examples:
        >>> print(sum(11.5,0.5))
        12.0

        >>> print(sum(100.5,1.5))
        Traceback Error
    """
    assert isinstance(a,float)
    assert isinstance(b,float)

    if (a > 100.0) or (a <-100.0) or (b > 100.0) or (b < 100.0):
        raise ValueError
    return a + b
