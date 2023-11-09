from enum import Enum
import sys


class AuditLevel(Enum):
    ERROR = 4
    INFO = 3
    DEBUG = 2
    TRACE = 1


class Audit:
    audit_level: AuditLevel

    def __init__(self, audit_level: AuditLevel, audit_file=None):
        self.audit_level = audit_level
        if audit_file:
            self.audit_file = open(audit_file, "w")
        else:
            self.audit_file = sys.stderr

    def error(self, message: str):
        if self.audit_level.value <= AuditLevel.ERROR.value:
            print("ERROR ", message, file=self.audit_file)

    def info(self, message: str):
        if self.audit_level.value <= AuditLevel.INFO.value:
            print("INFO  ", message, file=self.audit_file)

    def debug(self, message: str):
        if self.audit_level.value <= AuditLevel.DEBUG.value:
            print("DEBUG ", message, file=self.audit_file)

    def trace(self, message: str):
        if self.audit_level.value <= AuditLevel.TRACE.value:
            print("TRACE ", message, file=self.audit_file)

    def set_verbosity(self, verbosity: int):
        if verbosity >= AuditLevel.ERROR.value:
            self.audit_level = AuditLevel.TRACE
        else:
            self.audit_level = AuditLevel(AuditLevel.ERROR.value - verbosity)
