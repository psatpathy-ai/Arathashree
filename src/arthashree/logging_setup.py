from __future__ import annotations

import json
import logging
import sys
from typing import Any, Dict


class JsonLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = self.extra.copy()
        if isinstance(msg, dict):
            obj = {**extra, **msg}
            return json.dumps(obj, default=str), kwargs
        return json.dumps({"msg": msg, **extra}, default=str), kwargs


def get_logger(name: str, *, level: int = logging.INFO, extra: Dict[str, Any] | None = None) -> JsonLoggerAdapter:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler(stream=sys.stdout)
        fmt = logging.Formatter("%(message)s")
        h.setFormatter(fmt)
        logger.addHandler(h)
    logger.setLevel(level)
    return JsonLoggerAdapter(logger, extra or {})
