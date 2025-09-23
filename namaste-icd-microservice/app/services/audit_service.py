import logging
import os
from datetime import datetime
import json

from app.config import settings

logger = logging.getLogger(__name__)

class AuditService:
    def __init__(self):
        # Ensure audit directory exists
        self.audit_dir = os.path.join(settings.output_dir, "audit_logs")
        os.makedirs(self.audit_dir, exist_ok=True)

    async def log_access(self, user_id: str, operation: str, resource_id: str, timestamp: str = None):
        """
        Log successful access or operation.
        """
        entry = {
            "type": "access",
            "user_id": user_id,
            "operation": operation,
            "resource_id": resource_id,
            "timestamp": timestamp or datetime.utcnow().isoformat()
        }
        await self._write_log(entry)

    async def log_error(self, request, error, timestamp: str = None):
        """
        Log an error, including request details and exception info.
        """
        entry = {
            "type": "error",
            "path": request.url.path,
            "method": request.method,
            "error_code": getattr(error, "status_code", "N/A"),
            "error_message": str(error),
            "timestamp": timestamp or datetime.utcnow().isoformat()
        }
        await self._write_log(entry)

    async def _write_log(self, entry: dict):
        """
        Internal helper to append a log entry as JSON.
        """
        date_str = entry["timestamp"][:10]
        file_path = os.path.join(self.audit_dir, f"audit_{date_str}.log")
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
