import logging

from google.cloud import logging_v2
from google.cloud.logging.handlers import CloudLoggingHandler


loggers = {}


class Logger(object):
    def __init__(self, log_name):
        global loggers

        if loggers.get(log_name):
            self.logger = loggers.get(log_name)
        else:
            stream_handler = logging.StreamHandler()
            log_client = logging_v2.Client()
            gcloud_logging_handler = CloudLoggingHandler(log_client, name=log_name)
            self.logger = logging.getLogger(log_name)
            self.logger.addHandler(gcloud_logging_handler)
            self.logger.addHandler(stream_handler)
            loggers[log_name] = self.logger
