from abc import ABC, abstractmethod
from typing import List
from services.discovery.domain.source import Source
from services.discovery.domain.scan_result import ScanResult

class Scanner(ABC):
    """
    Abstract interface for all discovery scanners.
    A scanner's sole responsibility is to observe and describe what exists in a source.
    It does not persist data and does not infer relationships.
    """
    
    def __init__(self, source: Source):
        self.source = source

    @abstractmethod
    def scan(self) -> List[ScanResult]:
        """
        Executes the scan against the configured source.
        Returns a list of ScanResults containing deterministic schemas and dataset details.
        """
        pass
