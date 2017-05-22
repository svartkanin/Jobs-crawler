from Jobs_Crawler import Crawler
from bs4 import BeautifulSoup
from collections import defaultdict
import json
import dateutil.parser
from datetime import datetime


class MonsterCrawler(Crawler):

	def __init__(self):
		url_parts = ['http://www.monster.se/jobb/sok/?q=', '&where=' + self.search_location[0] + '&sort=dt.rv.di']
		urls = defaultdict(list)

		for search in self.search_parameters:
			url = url_parts[0] + '-'.join(search) + url_parts[1]
			urls[" ".join(search)].append(url)

		super(MonsterCrawler, self).__init__(urls)


	def check_pagination(self, url, source_code):
		soup = BeautifulSoup(source_code, 'html.parser')
		pages = set()

		total_pages = soup.find('input', attrs={'id': 'totalPages'})
		if total_pages:
			value = total_pages['value']
			pages = [i for i in range(2, int(value)+1)]

		pages = sorted(pages)
		parameter_page = [['', '&page=' + str(page), page] for page in pages]

		return parameter_page


	def extract_jobs_from_source(self, source_code):
		webpage = 'Monster'
		jobs = []
		soup = BeautifulSoup(source_code, 'html.parser')
		entries = soup.select("script[type=application/ld+json]")

		for entry in entries:
			if str(entry.text.strip()):
				entry_json = json.loads(entry.text)

				if entry_json['@type'] == 'JobPosting':
					job_title = ''
					job_location = ''
					job_company = ''
					online = ''
					link = ''

					job_title = entry_json['title']
					link = entry_json['url']

					# if entry_json['hiringOrganization'] and entry_json['hiringOrganization']['name']:
					job_company = entry_json['hiringOrganization']['name']

					address = entry_json['jobLocation']['address']
					job_location = address['addressLocality'] + ', ' + address['addressRegion']

					# 2016-11-01T14:04:00+01:00
					timestamp = entry_json['datePosted']
					now = datetime.now()
					past = dateutil.parser.parse(timestamp).replace(tzinfo=None)

					diff = now - past
					if diff.days != 0:
						online = str(diff.days)
					else:
						online = str(diff.seconds / 86400.0)  # seconds of a 24h day

					if job_title and online and job_company and job_location and float(online) < self._max_days:
						jobs.append([webpage, job_title, job_location, job_company, str(online), link])

		return jobs


	def start_crawling(self):
		print("Start %s..." % __name__)
		return super(MonsterCrawler, self).start_crawling()
