import logging
import os


def setup_logging():
	log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

	log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

	handlers = [
		logging.StreamHandler(),
		logging.FileHandler('orchestrator.log')
	]

	logging.basicConfig(
		level=getattr(logging, log_level, logging.INFO),
		format=log_format,
		handlers=handlers
	)

	logger = logging.getLogger(__name__)
	logger.info("Logging configuration initialized")

	return logger




