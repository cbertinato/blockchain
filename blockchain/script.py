from functools import wraps

from blockchain.etc import (read_varint, little_endian_to_int, int_to_little_endian, encode_varint,
                            hash160)
from blockchain.op import OP_CODE_FUNCTIONS, OP_CODE_NAMES


def script_template(f):
    @wraps(f)
    def wrapper(cls, *args, **kwargs):
        cmd_stack = f(cls, *args, **kwargs)
        cmds = []
        for cmd in cmd_stack:
            if isinstance(cmd, str):
                cmds.append(OP_CODE_NAMES[cmd])
            else:
                cmds.append(cmd)

        return cls(cmds)

    return wrapper


class Script:
    def __init__(self, cmds=None):
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds

    def __repr__(self):
        cmds = []
        for cmd in self.cmds:
            if isinstance(cmd, int):
                cmds.append(OP_CODE_FUNCTIONS[cmd])
            else:
                cmds.append(''.join('{:02x}'.format(x) for x in cmd))

        return repr(cmds)

    @classmethod
    def parse(cls, s):
        # script serialization always starts with the length of the entire script
        length = read_varint(s)

        cmds = []
        count = 0

        while count < length:
            current_byte = s.read(1)[0]
            count += 1

            # next n bytes are an element
            if 1 <= current_byte <= 75:
                cmds.append(s.read(current_byte))
                count += current_byte

            # OP_PUSHDATA1
            elif current_byte == 76:
                data_length = little_endian_to_int(s.read(1))
                cmds.append(s.read(data_length))
                count += data_length + 1

            # OP_PUSHDATA2
            elif current_byte == 77:
                data_length = little_endian_to_int(s.read(2))
                cmds.append(s.read(data_length))
                count += data_length + 2

            # it's an op code
            else:
                cmds.append(current_byte)

        if count != length:
            raise SyntaxError('parsing script failed')

        return cls(cmds)

    def raw_serialize(self):
        result = b''

        for cmd in self.cmds:
            # if it's an int, then it is an opcode
            if isinstance(cmd, int):
                result += int_to_little_endian(cmd, 1)
            else:
                length = len(cmd)

                if length < 75:
                    result += int_to_little_endian(length, 1)

                elif 75 < length < 256:
                    result += int_to_little_endian(76, 1)
                    result += int_to_little_endian(length, 1)

                elif 256 <= length <= 520:
                    result += int_to_little_endian(77, 1)
                    result += int_to_little_endian(length, 2)

                else:
                    raise ValueError('cmd too long')

                result += cmd

        return result

    def serialize(self):
        result = self.raw_serialize()
        length = len(result)
        return encode_varint(length) + result

    def __add__(self, other):
        return Script(self.cmds + other.cmds)

    def evaluate(self, z):
        cmds = self.cmds.copy()
        stack = []
        altstack = []

        while cmds:
            cmd = cmds.pop(0)

            if isinstance(cmd, int):
                operation = OP_CODE_FUNCTIONS[cmd]
                args = [stack]

                # OP_IF, OP_NOTIF
                if cmd in (99, 100):
                    args += [cmds]

                # OP_TOALTSTACK, OP_FROMALTSTACK
                elif cmd in (107, 108):
                    args += [altstack]

                # OP_CHECKSIG, OP_CHECKSIGVERIFY, OP_CHECKMULTISIG, OP_CHECKMULTISIGVERIFY
                elif cmd in (172, 173, 174, 175):
                    args += [z]

                if not operation(*args):
                    # TODO: add logging here
                    print('bad op: {!r}'.format(operation))
                    return False

            else:
                stack.append(cmd)

        if not stack or not stack.pop():
            return False

        return True

    @classmethod
    @script_template
    def p2pkh(cls, pk_hash: bytes):
        return ['OP_DUP', 'OP_HASH160', pk_hash, 'OP_EQUALVERIFY', 'OP_CHECKSIG']
