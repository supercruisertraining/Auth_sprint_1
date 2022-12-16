import logging

import logstash
from flask import request

from core.config import config

custom_logger = logging.getLogger(__name__)
custom_logger.setLevel(logging.INFO)
logstash_handler = logstash.LogstashHandler(config.LOGSTASH_HOST, config.LOGSTASH_PORT, version=1)


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request.headers.get('X-Request-Id')
        return True


custom_logger.addFilter(RequestIdFilter())
custom_logger.addHandler(logstash_handler)
