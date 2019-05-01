from functools import wraps
from dataclasses import dataclass
from typing import Any

from blockchain.etc import hash160, hash256
from blockchain.crypto import S256Point, Signature


OP_CODE_FUNCTIONS = {}
OP_CODE_NAMES = {}


# def opcode(n, name, min_stack=1):
#     def wrapper(f):
#         OP_CODE_FUNCTIONS[n] = (f, name)
#         OP_CODE_NAMES[name] = n
#
#         if min_stack > 0:
#             @wraps(f)
#             def func(stack, *args):
#                 if len(stack) < min_stack:
#                     return False
#                 return f(stack, *args)
#             return func
#         else:
#             @wraps(f)
#             def func(stack, *args):
#                 return f(stack, *args)
#             return func
#
#     return wrapper


@dataclass(eq=True, frozen=True)
class OpCode:
    label: str
    num: int
    func: Any
    min_stack: int

    def __post_init__(self):
        OP_CODE_FUNCTIONS[self.num] = self
        OP_CODE_NAMES[self.label] = self.num

    def __call__(self, stack, *args, **kwargs):
        if self.min_stack > 0 and len(stack) < self.min_stack:
            return False
        else:
            return self.func(stack, *args)

    def __repr__(self):
        return self.label

    @property
    def hex(self):
        return '{:02x}'.format(self.num)


def opcode(num, label, min_stack=1):
    def wrapper(f):
        return OpCode(label=label, num=num, func=f, min_stack=min_stack)
    return wrapper


def encode_num(num):
    if num == 0:
        return b''
    abs_num = abs(num)
    negative = num < 0
    result = bytearray()
    while abs_num:
        result.append(abs_num & 0xff)
        abs_num >>= 8
    if result[-1] & 0x80:
        if negative:
            result.append(0x80)
        else:
            result.append(0)
    elif negative:
        result[-1] |= 0x80
    return bytes(result)


def decode_num(element):
    if element == b'':
        return 0
    big_endian = element[::-1]
    if big_endian[0] & 0x80:
        negative = True
        result = big_endian[0] & 0x7f
    else:
        negative = False
        result = big_endian[0]
    for c in big_endian[1:]:
        result <<= 8
        result += c
    if negative:
        return -result
    else:
        return result


@opcode(0, 'OP_0', min_stack=0)
def op_0(stack):
    stack.append(encode_num(0))
    return True


@opcode(118, 'OP_DUP')
def op_dup(stack):
    stack.append(stack[-1])
    return True


@opcode(169, 'OP_HASH160')
def op_hash160(stack):
    el = stack.pop()
    stack.append(hash160(el))
    return True


@opcode(170, 'OP_HASH256')
def op_hash256(stack):
    el = stack.pop()
    stack.append(hash256(el))
    return True


@opcode(172, 'OP_CHECKSIG', min_stack=2)
def op_checksig(stack, z):
    sec_pubkey = stack.pop()
    der_signature = stack.pop()[:-1]

    try:
        point = S256Point.parse(sec_pubkey)
        sig = Signature.parse(der_signature)
    except (ValueError, SyntaxError):
        return False

    if point.verify(z, sig):
        stack.append(encode_num(1))
    else:
        stack.append(encode_num(0))
    print(f'opchecksig: {stack}')
    return True


@opcode(136, 'OP_EQUALVERIFY', min_stack=2)
def op_equalverify(stack):
    if stack.pop() != stack.pop():
        return False
    return True


@opcode(99, 'OP_IF')
def op_if(stack, cmds):
    raise NotImplementedError('OP_IF')


@opcode(100, 'OP_NOTIF')
def op_notif(stack, cmds):
    raise NotImplementedError('OP_NOTIF')


@opcode(107, 'OP_TOALTSTACK')
def op_toaltstack(stack, altstack):
    raise NotImplementedError('OP_TOALTSTACK')
