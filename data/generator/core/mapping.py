import hashlib
import struct

class IDMapper:
    """Deterministic mapper from canonical IDs to historical IDs."""
    
    @staticmethod
    def to_legacy_int(canonical_id: str) -> int:
        """Deterministically map a canonical ID (e.g. CUST_00001) to a legacy integer."""
        h = hashlib.md5(canonical_id.encode()).digest()
        # use first 4 bytes for an integer
        return struct.unpack("<I", h[:4])[0] % 10000000
        
    @staticmethod
    def to_uuid(canonical_id: str) -> str:
        """Deterministically map a canonical ID to a UUID."""
        h = hashlib.md5(canonical_id.encode()).hexdigest()
        return f"{h[:8]}-{h[8:12]}-4{h[13:16]}-a{h[17:20]}-{h[20:32]}"
