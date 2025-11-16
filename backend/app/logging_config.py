import logging
import json
import sys
from datetime import datetime, timezone
from . import config as conf


class JSONFormatter(logging.Formatter):
    def format(self, record):
        # base record
        record_dict = {
            # Use timezone-aware UTC timestamp instead of deprecated utcfromtimestamp()
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # include extra fields if present on the record
        for k, v in record.__dict__.items():
            if k in ("msg", "args", "levelname", "levelno", "name", "created", "msecs", "relativeCreated", "stack_info", "exc_info", "exc_text", "pathname", "filename", "module", "lineno", "funcName", "process", "processName", "thread", "threadName"):
                continue
            try:
                json.dumps({k: v})
                record_dict[k] = v
            except Exception:
                # fallback to string
                try:
                    record_dict[k] = str(v)
                except Exception:
                    record_dict[k] = None

        return json.dumps(record_dict, ensure_ascii=False)


def configure_logging():
    level = getattr(logging, conf.LOG_LEVEL.upper(), logging.INFO)
    root = logging.getLogger()
    # clear existing handlers
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    if conf.LOG_JSON:
        handler.setFormatter(JSONFormatter())
    else:
        fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
        handler.setFormatter(logging.Formatter(fmt))

    root.addHandler(handler)
    root.setLevel(level)


__all__ = ["configure_logging"]
