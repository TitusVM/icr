from __future__ import division
from binascii import unhexlify as uh
import binascii
import sys
import hashlib
import os
import time
from base64 import b64encode
from base64 import b64decode

flag = b"My grade in ICR is 6.0"

def to_bytes(n, length, byteorder='big'):
    # Same as Python 3's int.to_bytes, but for Python 2 compat
    h = '%x' % n
    s = binascii.unhexlify(('0' * (len(h) % 2) + h).zfill(length * 2))
    return s if byteorder == 'big' else s[::-1]


def sqrt4k3(x, p):
    # Compute candidate square root of x modulo p, with p = 3 (mod 4).
    return pow(x, (p + 1) // 4, p)


def sqrt8k5(x, p):
    # Compute candidate square root of x modulo p, with p = 5 (mod 8).
    y = pow(x, (p + 3) // 8, p)
    # If the square root exists, it is either y or y*2^(p-1)/4.
    if (y * y) % p == x % p:
        return y
    else:
        z = pow(2, (p - 1) // 4, p)
        return (y * z) % p


def from_le2(s, le=True):
    value = 0
    for i, b in enumerate(bytearray(s)):
        m = i if le else (len(s) - i - 1)
        value += b << (8 * m)
    return value


def hexi(s):
    # Decode a hexadecimal string representation of the integer.
    if sys.version_info > (3, 0):
        r = int.from_bytes(bytes.fromhex(s), byteorder="big")
    else:
        r = from_le2(binascii.unhexlify(s), le=False)
    return r


def rol(x, b):
    # Rotate a word x by b places to the left.
    return ((x << b) | (x >> (64 - b))) & (2**64 - 1)


def from_le(s):
    # From little endian.
    if sys.version_info > (3, 0):
        r = int.from_bytes(s, byteorder="little")
    else:
        r = from_le2(s)
    return r



class Field(object):
    # A (prime) field element.
    def __init__(self, x, p):
        # Construct number x (mod p).
        self.__x = x % p
        self.__p = p

    def __check_fields(self, y):
        # Check that fields of self and y are the same.
        if not isinstance(y, Field) or self.__p != y.__p:
            raise ValueError("Fields don't match")

    def __add__(self, y):
        # Field addition.  The fields must match.
        self.__check_fields(y)
        return Field(self.__x + y.__x, self.__p)

    def __sub__(self, y):
        # Field subtraction.  The fields must match.
        self.__check_fields(y)
        return Field(self.__p + self.__x - y.__x, self.__p)

    def __neg__(self):
        # Field negation.
        return Field(self.__p - self.__x, self.__p)

    def __mul__(self, y):
        # Field multiplication.  The fields must match.
        self.__check_fields(y)
        return Field(self.__x * y.__x, self.__p)

    def __truediv__(self, y):
        # Field division.  The fields must match.
        return self * y.inv()

    def inv(self):
        # Field inverse (inverse of 0 is 0).
        return Field(pow(self.__x, self.__p - 2, self.__p), self.__p)

    def sqrt(self):
        # Field square root.  Returns none if square root does not exist.
        # Note: not presently implemented for p mod 8 = 1 case.
        # Compute candidate square root.
        if self.__p % 4 == 3:
            y = sqrt4k3(self.__x, self.__p)
        elif self.__p % 8 == 5:
            y = sqrt8k5(self.__x, self.__p)
        else:
            raise NotImplementedError("sqrt(_,8k+1)")
        _y = Field(y, self.__p)
        # Check square root candidate valid.
        return _y if _y * _y == self else None

    def make(self, ival):
        # Make the field element with the same field as this, but
        # with a different value.
        return Field(ival, self.__p)

    def iszero(self):
        # Is the field element the additive identity?
        return self.__x == 0

    def __eq__(self, y):
        # Are field elements equal?
        return self.__x == y.__x and self.__p == y.__p

    def __ne__(self, y):
        # Are field elements not equal?
        return not (self == y)

    def tobytes(self, b):
        # Serialize number to b-1 bits.
        return to_bytes(self.__x, b // 8, byteorder="little")

    def frombytes(self, x, b):
        # Unserialize number from bits.
        rv = from_le(x) % (2**(b - 1))
        return Field(rv, self.__p) if rv < self.__p else None

    def sign(self):
        # Compute sign of number, 0 or 1.  The sign function
        # has the following property:
        # sign(x) = 1 - sign(-x) if x != 0.
        return self.__x % 2


class EdwardsPoint(object):
    # A point on (twisted) Edwards curve.

    def initpoint(self, x, y):
        self.x = x
        self.y = y
        self.z = self.base_field.make(1)

    def decode_base(self, s, b):
        # Check that point encoding is the correct length.
        if len(s) != b // 8:
            return (None, None)
        # Extract signbit.
        s = bytearray(s)
        xs = s[(b - 1) // 8] >> ((b - 1) & 7)
        # Decode y.  If this fails, fail.
        y = self.base_field.frombytes(s, b)
        if y is None:
            return (None, None)
        # Try to recover x.  If it does not exist, or if zero and xs
        # are wrong, fail.
        x = self.solve_x2(y).sqrt()
        if x is None or (x.iszero() and xs != x.sign()):
            return (None, None)
        # If sign of x isn't correct, flip it.
        if x.sign() != xs:
            x = -x
        # Return the constructed point.
        return (x, y)

    def encode_base(self, b):
        xp, yp = self.x / self.z, self.y / self.z
        # Encode y.
        s = bytearray(yp.tobytes(b))
        # Add sign bit of x to encoding.
        if xp.sign() != 0:
            s[(b - 1) // 8] |= 1 << (b - 1) % 8
        return s

    def __mul__(self, x):
        r = self.zero_elem()
        s = self
        while x > 0:
            if (x % 2) > 0:
                r = r + s
            s = s.double()
            x = x // 2
        return r

    def __eq__(self, y):
        # Check that two points are equal.
        # Need to check x1/z1 == x2/z2 and similarly for y, so cross
        # multiply to eliminate divisions.
        xn1 = self.x * y.z
        xn2 = y.x * self.z
        yn1 = self.y * y.z
        yn2 = y.y * self.z
        return xn1 == xn2 and yn1 == yn2

    def __ne__(self, y):
        # Check if two points are not equal.
        return not (self == y)


class Edwards25519Point(EdwardsPoint):
    # A point on Edwards25519.
    # Create a new point on the curve.
    base_field = Field(1, 2**255 - 19)
    d = -base_field.make(121665) / base_field.make(121666)
    f0 = base_field.make(0)
    f1 = base_field.make(1)
    xb = base_field.make(hexi("216936D3CD6E53FEC0A4E231FDD6DC5C692CC76" +
                              "09525A7B2C9562D608F25D51A"))
    yb = base_field.make(hexi("666666666666666666666666666666666666666" +
                              "6666666666666666666666658"))

    @staticmethod
    def stdbase():
        # The standard base point.
        return Edwards25519Point(Edwards25519Point.xb,
                                 Edwards25519Point.yb)

    def __init__(self, x, y):
        # Check the point is actually on the curve.
        if y * y - x * x != self.f1 + self.d * x * x * y * y:
            raise ValueError("Invalid point")
        self.initpoint(x, y)
        self.t = x * y

    def decode(self, s):
        # Decode a point representation.
        x, y = self.decode_base(s, 256)
        return Edwards25519Point(x, y) if x is not None else None

    def encode(self):
        # Encode a point representation.
        return self.encode_base(256)

    def zero_elem(self):
        # Construct a neutral point on this curve.
        return Edwards25519Point(self.f0, self.f1)

    def solve_x2(self, y):
        # Solve for x^2.
        return ((y * y - self.f1) / (self.d * y * y + self.f1))

    def __add__(self, y):
        # Point addition.
        # The formulas are from EFD.
        tmp = self.zero_elem()
        zcp = self.z * y.z
        A = (self.y - self.x) * (y.y - y.x)
        B = (self.y + self.x) * (y.y + y.x)
        C = (self.d + self.d) * self.t * y.t
        D = zcp + zcp
        E, H = B - A, B + A
        F, G = D - C, D + C
        tmp.x, tmp.y, tmp.z, tmp.t = E * F, G * H, F * G, E * H
        return tmp

    def double(self):
        # Point doubling.
        # The formulas are from EFD (with assumption a=-1 propagated).
        tmp = self.zero_elem()
        A = self.x * self.x
        B = self.y * self.y
        Ch = self.z * self.z
        C = Ch + Ch
        H = A + B
        xys = self.x + self.y
        E = H - xys * xys
        G = A - B
        F = C + G
        tmp.x, tmp.y, tmp.z, tmp.t = E * F, G * H, F * G, E * H
        return tmp

    def l(self):
        # Order of basepoint.
        return hexi("1000000000000000000000000000000014def9dea2f79cd" +
                    "65812631a5cf5d3ed")

    def c(self):
        # The logarithm of cofactor.
        return 3

    def n(self):
        # The highest set bit
        return 254

    def b(self):
        # The coding length
        return 256

    def is_valid_point(self):
        # Validity check (for debugging)
        x, y, z, t = self.x, self.y, self.z, self.t
        x2 = x * x
        y2 = y * y
        z2 = z * z
        lhs = (y2 - x2) * z2
        rhs = z2 * z2 + self.d * x2 * y2
        assert(lhs == rhs)
        assert(t * z == x * y)



class PureEdDSA(object):
    # PureEdDSA scheme.
    # Limitation: only b mod 8 = 0 is handled.
    def __init__(self, B, H):
        # Create a new object.
        self.B = B
        self.H = H
        self.l = self.B.l()
        self.n = self.B.n()
        self.b = self.B.b()
        self.c = self.B.c()

    def __clamp(self, a):
        # Clamp a private scalar.
        _a = bytearray(a)
        for i in range(0, self.c):
            _a[i // 8] &= ~(1 << (i % 8))
        _a[self.n // 8] |= 1 << (self.n % 8)
        for i in range(self.n + 1, self.b):
            _a[i // 8] &= ~(1 << (i % 8))
        return _a

    def keygen(self, privkey):
        # Generate a key.  If privkey is None, a random one is generated.
        # In any case, the (privkey, pubkey) pair is returned.
        # If no private key data is given, generate random.
        if privkey is None:
            privkey = os.urandom(self.b // 8)

        # Expand key.
        khash = self.H(privkey, None, None)
        a = from_le(self.__clamp(khash[:self.b // 8]))
        # Return the key pair (public key is A=Enc(aB).
        return privkey, (self.B * a).encode()

    
    
    def sign(self, privkey, pubkey, msg, ctx, hflag):
        # Sign with key pair.
        # Expand key.
        khash = self.H(privkey, None, None)
        a = from_le(self.__clamp(khash[:self.b // 8]))
        seed = khash[self.b // 8:]
        # Calculate r and R (R only used in encoded form).
        r = from_le(self.H(seed + msg, ctx, hflag)) % self.l
        R = (self.B * r).encode()
        # Calculate h.
        h = from_le(self.H(R + pubkey + msg, ctx, hflag)) % self.l
        # Calculate s.
        S = to_bytes(((r + h * r) % self.l), self.b // 8, byteorder="little")
        # In RFC: S = ((r + h * a) % self.l).to_bytes(self.b // 8, byteorder="little")

        # The final signature is a concatenation of R and S.
        return R + S



    
    def verify(self, pubkey, msg, sig, ctx, hflag):
        # Verify signature with public key.
        # Sanity-check sizes.
        if len(sig) != self.b // 4:
            return False
        if len(pubkey) != self.b // 8:
            return False
        # Split signature into R and S, and parse.
        Rraw, Sraw = sig[:self.b // 8], sig[self.b // 8:]
        R, S = self.B.decode(Rraw), from_le(Sraw)
        # Parse public key.
        A = self.B.decode(pubkey)
        # Check parse results.
        if (R is None) or (A is None) or S >= self.l:
            return False
        # Calculate h.
        h = from_le(self.H(Rraw + pubkey + msg, ctx, hflag)) % self.l
        # Calculate left and right sides of check eq.
        rhs = R + (R * h)
        lhs = self.B * S
        for _ in range(0, self.c):
            lhs = lhs.double()
            rhs = rhs.double()
        # Check eq. holds?
        return lhs == rhs


def Ed25519_inthash(data, ctx, hflag):
    if (ctx is not None and len(ctx) > 0) or hflag:
        raise ValueError("Contexts/hashes not supported")
    return hashlib.sha512(data).digest()





class EdDSA(object):
    # EdDSA scheme.
    # Create a new scheme object, with the specified PureEdDSA base
    # scheme and specified prehash.
    def __init__(self, pure_scheme, prehash=None):
        self.__pflag = False
        self.__pure = pure_scheme
        self.__prehash = None
        if prehash is not None:
            self.__pflag = True
            self.__prehash, self.__prehash_digest_args = prehash

        self.reset()

    def reset(self):
        if self.__prehash is not None:
            self.__prehashctx = self.__prehash()

    def keygen(self, privkey):
        # Generate a key.  If privkey is none, it generates a random
        # privkey key, otherwise it uses a specified private key.
        # Returns pair (privkey, pubkey).
        return self.__pure.keygen(privkey)

    def update(self, data):
        # Update the prehash with chunks of data
        if self.__prehash is not None:
            self.__prehashctx.update(data)
            
      
            
    def sign(self, privkey, pubkey, msg, ctx=None):
        # Sign message msg using specified key pair.
        if ctx is None:
            ctx = b""
        self.update(msg)
        msgdigest = self.__prehashctx.digest(*self.__prehash_digest_args) if self.__prehash is not None else msg
        r = self.__pure.sign(privkey, pubkey, msgdigest,
                             ctx, self.__pflag)
        self.reset()
        return r

    def verify(self, pubkey, msg, sig, ctx=None):
        # Verify signature sig on message msg using public key pubkey.
        if ctx is None:
            ctx = b""
        self.update(msg)
        msgdigest = self.__prehashctx.digest(*self.__prehash_digest_args) if self.__prehash is not None else msg
        r = self.__pure.verify(pubkey, msgdigest, sig,
                               ctx, self.__pflag)
        self.reset()
        return r


# The base PureEdDSA schemes.
pEd25519 = PureEdDSA(B=Edwards25519Point.stdbase(),
                     H=Ed25519_inthash)

# Our signature schemes.
class Ed25519(EdDSA):
    def __init__(self):
        super(Ed25519, self).__init__(pEd25519)


def test():
    ed = Ed25519()
    (prv, pub) = ed.keygen(None)
    prv = b'BtN7lbWbRBSoUH/QQ0YvEmaZtD8PPGuUwP5jGou/4fk='
    pub = b'myakZsjn1etG5Tbo6z8FB9Ilf0XPKUThDgC070xjCRE='
    print("prv1 = %s" % b64encode(prv), file=sys.stderr)
    print("pub1 = %s" % b64encode(pub))
    msg = b"Grade of Alexandre Duc at ICR = 6.0"
    sig = ed.sign(prv, pub, msg)
    print("m1 = %s" % msg)
    print("sig1 = %s" % b64encode(sig))
    #sanity check
    print(ed.verify(pub,msg, sig))


def exploit():
    ed = Ed25519()
    # We know Alexandre uses the following public key and signed the message
    pub_known = b64decode(b'JLPz0zQJocxpEORBf/1rDf4oQFwtT96bU5bDvktWsLs=')
    msg_known = b"Grade of Alexandre Duc at ICR = 6.0"
    sig_known = b64decode(b'eHM1CCOb3K3oPYjVqEgbhG1UkBgMXVz0rgLPcFjm+SbJFsgGFb0bwqIl1Wxh9jTEXgW3ZKYKpp6osEF6041KCQ==')
    print("msg_known = %s" % msg_known)
    print("sig_known = %s" % b64encode(sig_known))
    print(ed.verify(pub_known, msg_known, sig_known))

    # We know that the signature implementation has a vulnerability, it doesn't use the private key
    # Extract R and S
    R_known = sig_known[:32]
    S_known = sig_known[32:]
    # Decode R to find r and calculate a
    r_known = from_le(R_known)
    h_known = from_le(Ed25519_inthash(R_known + pub_known + msg_known, None, False))
    # a is not used so we can use 32 random bytes
    a = os.urandom(32)

    # We forge a signature for 
    sig_new = pEd25519.sign(a, pub_known, flag, None, False)
    print("msg_new = %s" % flag)
    print("sig_new = %s" % b64encode(sig_new))
    print(ed.verify(pub_known, flag, sig_new))

exploit() 
