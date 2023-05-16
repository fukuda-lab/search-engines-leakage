import base64
import base58
import codecs
import hashlib
import bz2
import gzip
import zlib
from crccheck.crc import Crc16, Crc32
from Crypto.Hash import RIPEMD160

ENCODING_NAMES = [
    "original",  # 0
    "base16",  # 1
    "base32",  # 2
    "base32hex",  # 3
    "base58",  # 4
    "base64",  # 5
    "gzip",  # 6
    "bzip2",  # 7
    "deflate",  # 8
    "md5",  # 9
    "sha1",  # 10
    "sha224",  # 11
    "sha256",  # 12
    "sha384",  # 13
    "sha512",  # 14
    "sha3_224",  # 15
    "sha3_256",  # 16
    "sha3_384",  # 17
    "sha3_512",  # 18
    "blake2s",  # 19
    "blake2b",  # 20
    "ripemd_160",  # 21
    "crc16",  # 22
    "crc32",  # 23
    "adler32",  # 24
    "rot13",  # 25
]


class Encodings:
    def __init__(self, search_terms):
        self.encodings = dict()
        self.search_terms = search_terms
        for keyword in search_terms:
            self.encodings[keyword] = self._get_keyword_encodings(keyword)

    @staticmethod
    def _get_keyword_encodings(keyword):
        """Returns a list of encodings for a given keyword.
        Bear in mind that there are some encodings that are not reversible, so the original keyword cannot be recovered.
        Also, some encodings used here produce outputs that don't resemble the original keyword which may lead to false positives when searching for the keyword.
        """

        def process_hash_function(hash_function, utf_8_encoded_keyword):
            hasher = hash_function()
            hasher.update(utf_8_encoded_keyword)
            return hasher.hexdigest()

        def process_ripemd_hash_function(ripemd_hash, utf_8_encoded_keyword):
            hasher = ripemd_hash.new()
            hasher.update(utf_8_encoded_keyword)
            return hasher.hexdigest()

        def _deflate(utf_8_encoded_keyword):
            """Separate function because takes more than 1 line."""
            compressed_data = zlib.compress(utf_8_encoded_keyword)
            deflated_data = compressed_data[2:-4]  # Remove zlib header and footer
            encoded_deflated_data = base64.b64encode(deflated_data).decode(
                errors="ignore"
            )
            return encoded_deflated_data

        # Encodings: base16, base32, base32hex, base58, base64, gz, bzip2, deflate, md2, md4, md5, sha1, sha224, sha256, sha384, sha512, crc16, crc32, sha3_224, sh3_256, sh3_384, sh3_512, ripemd_128, ripemd_169, ripemd_256, ripemd_320,  whirlpool,  rot13, snefru128, snefru256,  adler32, blake2s, blake2b.
        utf_8_encoded_keyword = keyword.encode()
        encodings = dict()

        # Original keyword
        encodings["original"] = keyword

        # Base encodings
        encodings["base16"] = codecs.encode(utf_8_encoded_keyword, "hex").decode()
        encodings["base32"] = base64.b32encode(utf_8_encoded_keyword).decode()
        encodings["base32hex"] = base64.b16encode(utf_8_encoded_keyword).decode()
        encodings["base58"] = base58.b58encode(utf_8_encoded_keyword).decode()
        encodings["base64"] = base64.b64encode(utf_8_encoded_keyword).decode()

        # Compression algorithms (false-positive risky)
        encodings["gzip"] = gzip.compress(utf_8_encoded_keyword).decode(errors="ignore")
        encodings["bzip2"] = bz2.compress(utf_8_encoded_keyword).decode(errors="ignore")
        encodings["deflate"] = _deflate(utf_8_encoded_keyword)

        # Hash functions (false-positive risky)
        hash_functions = [
            ("md5", hashlib.md5),
            ("sha1", hashlib.sha1),
            ("sha224", hashlib.sha224),
            ("sha256", hashlib.sha256),
            ("sha384", hashlib.sha384),
            ("sha512", hashlib.sha512),
            ("sha3_224", hashlib.sha3_224),
            ("sha3_256", hashlib.sha3_256),
            ("sha3_384", hashlib.sha3_384),
            ("sha3_512", hashlib.sha3_512),
            ("blake2s", hashlib.blake2s),
            ("blake2b", hashlib.blake2b),
        ]

        for hash_name, hash_function in hash_functions:
            encodings[hash_name] = process_hash_function(
                hash_function, utf_8_encoded_keyword
            )

        # RIPEMD hash functions (false-positive risky)
        encodings["ripemd_160"] = process_ripemd_hash_function(
            RIPEMD160, utf_8_encoded_keyword
        )  # Most common and the only one with a working library found yet, missing 128, 250 and 320

        # Checksums (false-positive risky)
        encodings["crc16"] = str(Crc16.calc(utf_8_encoded_keyword))  # ?
        encodings["crc32"] = str(
            zlib.crc32(utf_8_encoded_keyword)
        )  # According to the official zlib docs, from 3.0, the result is always unsigned
        # encodings.append(str(Crc32.calc(utf_8_encoded_keyword))) # Another way to calculate CRC32
        encodings["adler32"] = str(
            zlib.adler32(utf_8_encoded_keyword)
        )  # According to the official zlib docs, from 3.0, the result is always unsigned

        # Other encodings
        encodings["rot13"] = codecs.encode(keyword, "rot_13")  # ?
        return encodings


# BEFORE MANUALLY CHECKING
# ENCODING_NAMES = [
#     "original",  # 0
#     "base16",  # 1
#     "base32",  # 2
#     "base32hex",  # 3
#     "base58",  # 4
#     "base64",  # 5
#     "gzip",  # 6
#     "bzip2",  # 7
#     "deflate",  # 8
#     "md5",  # 9
#     "sha1",  # 10
#     "sha224",  # 11
#     "sha256",  # 12
#     "sha384",  # 13
#     "sha512",  # 14
#     "sha3_224",  # 15
#     "sha3_256",  # 16
#     "sha3_384",  # 17
#     "sha3_512",  # 18
#     "blake2s",  # 19
#     "blake2b",  # 20
#     "ripemd_128",  # 21
#     "ripemd_160",  # 22
#     "ripemd_256",  # 23
#     "ripemd_320",  # 24
#     "crc16",  # 25
#     "crc32",  # 26
#     "adler32",  # 27
#     "rot13",  # 28
# ]
