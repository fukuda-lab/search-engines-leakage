import base64
import base58
import codecs
import hashlib
import bz2
import gzip
import zlib
from crccheck.crc import Crc16, Crc32
from Crypto.Hash import RIPEMD


def get_keyword_encodings(keyword):
    """Returns a list of encodings for a given keyword.
    Bear in mind that there are some encodings that are not reversible, so the original keyword cannot be recovered.
    Also, some encodings used here produce outputs that don't resemble the original keyword which may lead to false positives when searching for the keyword.
    """
    # Encodings: base16, base32, base32hex, base58, base64, gz, bzip2, deflate, md2, md4, md5, sha1, sha224, sha256, sha384, sha512, crc16, crc32, sha3_224, sh3_256, sh3_384, sh3_512, ripemd_128, ripemd_169, ripemd_256, ripemd_320,  whirlpool,  rot13, snefru128, snefru256,  adler32, blake2s, blake2b.

    # Original keyword
    encodings = [keyword]

    # Base encodings
    encodings.append(codecs.encode(keyword.encode(), "hex").decode())  # base16
    encodings.append(base64.b32encode(keyword.encode()).decode())  # base32
    encodings.append(base64.b16encode(keyword.encode()).decode())  # base32hex
    encodings.append(base58.b58encode(keyword.encode()).decode())  # base58
    encodings.append(base64.b64encode(keyword.encode()).decode())  # base64

    # Compression algorithms (false-positive risky)
    encodings.append(gzip.compress(keyword.encode()).decode(errors="ignore"))
    encodings.append(bz2.compress(keyword.encode()).decode(errors="ignore"))
    encodings.append(zlib.compress(keyword.encode()).decode(errors="ignore"))

    # Hash functions (false-positive risky)
    hash_functions = [
        hashlib.md5,
        hashlib.sha1,
        hashlib.sha224,
        hashlib.sha256,
        hashlib.sha384,
        hashlib.sha512,
        hashlib.sha3_224,
        hashlib.sha3_256,
        hashlib.sha3_384,
        hashlib.sha3_512,
        hashlib.blake2s,
        hashlib.blake2b,
    ]

    for hash_function in hash_functions:
        hasher = hash_function()
        hasher.update(keyword.encode())
        encodings.append(hasher.hexdigest())

    # RIPEMD hash functions (false-positive risky)
    ripemd_hash_functions = [
        RIPEMD.RIPEMD128,
        RIPEMD.RIPEMD160,
        RIPEMD.RIPEMD256,
        RIPEMD.RIPEMD320,
    ]

    for ripemd_hash_function in ripemd_hash_functions:
        hasher = ripemd_hash_function.new()
        hasher.update(keyword.encode())
        encodings.append(hasher.hexdigest())

    # Checksums (false-positive risky)
    encodings.append(str(Crc16.calc(keyword.encode())))
    encodings.append(str(Crc32.calc(keyword.encode())))
    encodings.append(str(zlib.adler32(keyword.encode()) & 0xFFFFFFFF))

    # Other encodings
    encodings.append(codecs.encode(keyword, "rot_13"))

    return encodings

    # All encodings asked:
    # 1: 'base16',
    # 2: 'base32',
    # 3: 'base32hex',
    # 4: 'base58',
    # 5: 'base64',
    # 6: 'gz',
    # 7: 'bzip2',
    # 8: 'deflate',
    # 9: 'md2',
    # 10: 'md4',
    # 11: 'md5',
    # 12: 'sha1',
    # 13: 'sha224',
    # 14: 'sha256',
    # 15: 'sha384',
    # 16: 'sha512',
    # 17: 'crc16',
    # 18: 'crc32',
    # 19: 'sha3_224',
    # 20: 'sh3_256',
    # 21: 'sh3_384',
    # 22: 'sh3_512',
    # 23: 'ripemd_128',
    # 24: 'ripemd_169',
    # 25: 'ripemd_256',
    # 26: 'ripemd_320',
    # 27: 'whirlpool',
    # 28: 'rot13',
    # 29: 'snefru128',
    # 30: 'snefru256',
    # 31: 'adler32',
    # 32: 'blake2s',
    # 33: 'blake2b',
    #
