"""
Finite fields

Intuitively, the fact that we have a prime order results in every element of a
finite field being equivalent. If the order of the set was a composite number,
multiplying the set by one of the divisors would result in a smaller set.

"""


class FieldElement:
    """
    Field element

    Examples
    --------

    **Equality**

    >>> a = FieldElement(7, 13)
    >>> b = FieldElement(6, 13)
    >>> print(a == b)
    False
    >>> print(a == a)
    True

    **Addition**

    >>> a = FieldElement(7, 13)
    >>> b = FieldElement(12, 13)
    >>> c = FieldElement(6, 13)
    >>> print(a+b==c)
    True

    ** Multiplication**

    >>> a = FieldElement(3, 13)
    >>> b = FieldElement(12, 13)
    >>> c = FieldElement(10, 13)
    >>> print(a*b==c)
    True

    ** Exponentiation **

    >>> a = FieldElement(3, 13)
    >>> b = FieldElement(1, 13)
    >>> print(a**3==b)
    True

    >>> a = FieldElement(7, 13)
    >>> b = FieldElement(8, 13)
    >>> print(a**-3==b)
    True

    ** Division **


    """
    def __init__(self, num, prime):
        if num < 0 or num >= prime:
            error = f'num={num} is not in field range 0 to {prime - 1}'
            raise ValueError(error)

        self.num = num
        self.prime = prime

    def __repr__(self):
        return f'FieldElement_{self.prime}({self.num})'

    def __eq__(self, other):
        if other is None:
            return False
        return self.prime == other.prime and self.num == other.num

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in different Fields')
        num = (self.num + other.num) % self.prime
        return self.__class__(num, self.prime)

    def __sub__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot subtract two numbers in different Fields')
        num = (self.num - other.num) % self.prime
        return self.__class__(num, self.prime)

    def __mul__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot multiply two numbers in different Fields')
        num = (self.num * other.num) % self.prime
        return self.__class__(num, self.prime)

    def __rmul__(self, other):
        return self.__class__(other, self.prime) * self

    def __pow__(self, exponent):
        n = exponent % (self.prime - 1)
        num = pow(self.num, n, self.prime)
        return self.__class__(num, self.prime)

    def __truediv__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot divide two numbers in different Fields')
        num = self.num * pow(other.num, self.prime - 2, self.prime) % self.prime
        return self.__class__(num, self.prime)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
