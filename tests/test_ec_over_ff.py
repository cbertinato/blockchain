import pytest

from blockchain.fields import FieldElement
from blockchain.elliptic import EllipticCurvePoint


def test_on_curve():
    prime = 223

    a = FieldElement(0, prime)
    b = FieldElement(7, prime)

    valid_points = ((192, 105), (17, 56), (1, 193))
    invalid_points = ((200, 119), (42, 99))

    for x_raw, y_raw in valid_points:
        x = FieldElement(x_raw, prime)
        y = FieldElement(y_raw, prime)

        EllipticCurvePoint(x, y, a, b)

    for x_raw, y_raw in invalid_points:
        x = FieldElement(x_raw, prime)
        y = FieldElement(y_raw, prime)

        with pytest.raises(ValueError):
            EllipticCurvePoint(x, y, a, b)


def test_addition():
    prime = 223
    a = FieldElement(0, prime)
    b = FieldElement(7, prime)

    x1 = FieldElement(170, prime)
    y1 = FieldElement(142, prime)
    x2 = FieldElement(60, prime)
    y2 = FieldElement(139, prime)

    p1 = EllipticCurvePoint(x1, y1, a, b)
    p2 = EllipticCurvePoint(x2, y2, a, b)

    result = p1 + p2
    expected = EllipticCurvePoint(FieldElement(220, prime), FieldElement(181, prime), a, b)

    assert result == expected


def test_scalar_multiply():
    prime = 223
    a = FieldElement(0, prime)
    b = FieldElement(7, prime)

    x = FieldElement(15, prime)
    y = FieldElement(86, prime)
    p = EllipticCurvePoint(x, y, a, b)

    result = 7 * p
    expected = EllipticCurvePoint(None, None, a, b)

    assert result == expected

    x = FieldElement(192, prime)
    y = FieldElement(105, prime)
    p = EllipticCurvePoint(x, y, a, b)

    result = 2 * p
    expected = p + p

    assert result == expected
