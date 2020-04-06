import importlib
import logging
import socket
import json

from crawler import Crawler

FORMAT = '%(asctime)-15s - [%(levelname)s] - %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

logger = logging.getLogger(__name__)


def _load_config(config_file):
	"""
	Load the configuration file
	
	Args:
	    config_file (str): Configuration file
	
	Returns:
	    dict: Content of the configuration file
	"""
	with open(config_file, 'r') as fp:
		return json.load(fp)

def _load_crawler(class_name, config_data):
	"""
	Load a specific website crawler
	
	Args:
	    class_name (str): Name of the webpage crawler
	    config_data (dict): Configuration data to be passed to the crawler
	
	Returns:
	    obj: New instance of the webpage crawler
	"""
	module = importlib.import_module('crawler')
	class_ = getattr(module, class_name)
	return class_(config_data)

def main():
	config_data = _load_config("config.json")
	crawler = Crawler(config_data)

	# crawl all defined websites
	for web in config_data.get("websites", []):
		try:
			web_obj = _load_crawler(web, config_data)
			crawler.setup(web_obj)
			crawler.fetch_html_listings()
		except ValueError as ve:
			logging.error(f'{web}: {ve}')
		# except Exception as e:
		# 	logging.error(e)

	# save found jobs to the database
	crawler.save_job_ads()
	# output new jobs to the output file
	crawler.output_new_jobs()


if __name__ == "__main__":
	main()
