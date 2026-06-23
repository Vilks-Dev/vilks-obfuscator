import logging
import sys
from contextvars import ContextVar

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="-")

class CorrelationIdFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = correlation_id_ctx.get()
        return True

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "correlation_id": "%(correlation_id)s", "message": "%(message)s"}'
    )
    handler.setFormatter(formatter)
    
    corr_filter = CorrelationIdFilter()
    handler.addFilter(corr_filter)
    
    logger.handlers = [handler]
