""" Elliptic curves """


class EllipticCurvePoint:
    """
    Points on an elliptic curve

    Examples
    --------
    >>> p1 = EllipticCurvePoint(-1, -1, 5, 7)
    >>> p2 = EllipticCurvePoint(-1, -2, 5, 7)
    Traceback (most recent call last):
        ...
    ValueError: (-1, -2) is not on the curve

    **Identity**

    >>> p1 = EllipticCurvePoint(-1, -1, 5, 7)
    >>> p2 = EllipticCurvePoint(-1, 1, 5, 7)
    >>> inf = EllipticCurvePoint(None, None, 5, 7)
    >>> print(p1 + inf)
    EllipticCurvePoint(-1, -1, 5, 7)
    >>> print(inf + p2)
    EllipticCurvePoint(-1, 1, 5, 7)
    >>> print(p1 + p2)
    EllipticCurvePoint(infinity)
    """

    def __init__(self, x, y, a, b):
        self.x = x
        self.y = y
        self.a = a
        self.b = b

        if x is None and y is None:
            return

        if not self.on_curve(x, y):
            raise ValueError(f'({x}, {y}) is not on the curve')

    def on_curve(self, x, y):
        return y ** 2 == x ** 3 + self.a * x + self.b

    def __repr__(self):
        if self.x is None and self.y is None:
            return f'EllipticCurvePoint(infinity)'
        else:
            return f'EllipticCurvePoint({self.x}, {self.y}, {self.a}, {self.b})'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        """
        Case 1: The points are in a vertical line or using the identity point
        Case 2: The points are not in a vertical line, but are different
        Case 3: The points are the same
        """
        if self.a != other.a or self.b != other.b:
            raise TypeError(f'Points {self}, {other} are not on the same curve')

        # Case 1
        # self is the additive identity
        if self.x is None:
            return other

        # other is the additive identity
        if other.x is None:
            return self

        # additive inverses
        if self.x == other.x and self.y != other.y:
            return self.__class__(None, None, self.a, self.b)

        # Case 2
        if self.x != other.x:
            slope = (other.y - self.y) / (other.x - self.x)
            x = slope ** 2 - self.x - other.x
            y = slope * (self.x - x) - self.y
            return self.__class__(x, y, self.a, self.b)

        # Case 3
        if self == other:
            # vertical line
            if self.y == 0 * self.x:
                return self.__class__(None, None, self.a, self.b)
            else:
                slope = (3 * self.x ** 2 + self.a) / (2 * self.y)
                x = slope ** 2 - 2 * self.x
                y = slope * (self.x - x) - self.y
                return self.__class__(x, y, self.a, self.b)

    def __rmul__(self, coefficient):
        coeff = coefficient
        current = self
        result = self.__class__(None, None, self.a, self.b)

        while coeff:
            if coeff & 1:
                result += current
            current += current
            coeff >>= 1

        return result


if __name__ == "__main__":
    import doctest
    doctest.testmod()
