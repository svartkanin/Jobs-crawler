from Jobs_Crawler import Crawler
from datetime import datetime
import dateutil.parser
from collections import defaultdict


class ArbetsfoermedlingenCrawler(Crawler):

	def __init__(self):
		url = "http://api.arbetsformedlingen.se/af/v0/platsannonser/matchning?antalrader=1000&lanid=1&nyckelord="
		urls = defaultdict(list)

		for search in self.search_parameters:
			urls[" ".join(search)].append(url + ' '.join(search))

		super(ArbetsfoermedlingenCrawler, self).__init__(urls, "JSON")


	def extract_jobs_from_source(self, json_data):
		webpage = 'Arbetsfoermedlingen'
		jobs = []

		if 'matchningslista' in json_data:
			match_l = json_data['matchningslista']
			if 'matchningdata' in match_l:
				match_d = match_l['matchningdata']

				for elem in match_d:
					job_title = ''
					job_location = ''
					job_company = ''
					online = ''
					link = ''

					job_title = elem['annonsrubrik']
					job_location = elem['lan']
					job_company = elem['arbetsplatsnamn']
					link = elem['annonsurl']

					online = elem['publiceraddatum']

					# 2016-11-01T14:04:00+01:00
					now = datetime.now()
					past = dateutil.parser.parse(online).replace(tzinfo=None)

					diff = now - past
					if diff.days != 0:
						online = diff.days
					else:
						online = diff.seconds / 86400.0

					if job_title and online and job_company and job_location and online < self._max_days:
						jobs.append([webpage, job_title, job_location, job_company, str(online), link])
				
		return jobs


	def start_crawling(self):
		print("Start %s..." % __name__)
		return super(ArbetsfoermedlingenCrawler, self).start_crawling()
