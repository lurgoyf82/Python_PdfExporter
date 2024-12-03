import logging

# Logger Class
class ServiceLogger:
    def __init__(self, log_file):
        self.setup_logging(log_file)

    def setup_logging(self, log_file):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s'
        )
        self.logger = logging.getLogger()

    def get_logger(self):
        return self.logger