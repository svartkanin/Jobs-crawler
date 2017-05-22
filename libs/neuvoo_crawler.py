from Jobs_Crawler import Crawler
from collections import defaultdict
import dateutil.parser
from datetime import datetime


class NeuvooCrawler(Crawler):

	def __init__(self):
		# Unfortunately 25 is the max limit of results that can be retrieved by using the API
		url_parts = ['http://api.neuvoo.com/apisearch?publisher=fe7ca91&q="',
					'&l=' + self.search_location[0] + '%2C+' + self.search_location[1] + \
					'&userip=1.2.3.4&useragent=Mozilla/%2F4.0(Firefox)&v=2&format=json&filter=24h&limit=25&sort=date']

		urls = defaultdict(list)

		for search in self.search_parameters:
			url = url_parts[0] + '+'.join(search) + url_parts[1]
			urls[" ".join(search)].append(url)

		super(NeuvooCrawler, self).__init__(urls, "JSON")


	def extract_jobs_from_source(self, json_data):
		webpage = 'Neuvoo'
		jobs = []

		if 'results' in json_data:
			results = json_data['results']

			for result in results:
				job_title = ''
				job_location = ''
				job_company = ''
				online = ''
				link = ''

				job_title = result['jobtitle']
				job_location = result['city']
				job_company = result['company']
				link = result['url']

				# has format: "Sun, 21 May 2017 02:00:01 -0400"
				timestamp = result['date']

				# 2016-11-01T14:04:00+01:00
				now = datetime.now()
				past = dateutil.parser.parse(online).replace(tzinfo=None)

				diff = now - past
				if diff.days != 0:
					online = str(diff.days)
				else:
					online = str(diff.seconds / 86400.0)  # seconds of a 24h day

				if job_title and job_company and job_location and float(online) < self._max_days:
					jobs.append([webpage, job_title, job_location, job_company, str(online), link])

		return jobs


	def start_crawling(self):
		print("Start %s..." % __name__)
		return super(NeuvooCrawler, self).start_crawling()
