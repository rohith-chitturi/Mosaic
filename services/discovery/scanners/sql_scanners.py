from typing import List
from services.discovery.scanners.base import Scanner
from services.discovery.domain.scan_result import ScanResult

class PostgresScanner(Scanner):
    def scan(self) -> List[ScanResult]:
        # TODO: Implement information_schema scanning
        return []

class MysqlScanner(Scanner):
    def scan(self) -> List[ScanResult]:
        # TODO: Implement information_schema scanning
        return []
