from Jobs_Crawler import Crawler
from bs4 import BeautifulSoup
from collections import defaultdict


class TheLocalCrawler(Crawler):

	def __init__(self):
		# Unfortunately only 25 results are displayed on the first site, more have to loaded with a Ajax(!?) call which is not implemented yet
		url_parts = ['http://www.thelocal.se/jobs/?job_keyword=', '&job_category=it&job_location=' + self.search_location[0] + '&date_posted=day']
		urls = defaultdict(list)

		for search in self.search_parameters:
			url = url_parts[0] + '+'.join(search) + url_parts[1]
			urls[" ".join(search)].append(url)

		super(TheLocalCrawler, self).__init__(urls, "RELOAD")


	def extract_jobs_from_source(self, source_code):
		jobs = []
		soup = BeautifulSoup(source_code, 'html.parser')

		div_elements = soup.find_all("div", attrs={"class": "job_container"})

		for div in div_elements:
			sub_element = div.find('a')
			webpage = sub_element['data-source'].strip()
			link = sub_element['href'].strip()

			div_title = div.find("div", attrs={"class": "jobstitle"})
			job_title = ''
			if div_title:
				job_title = div_title.text.strip()

			div_company = div.find("div", attrs={"class": "job_company"})
			job_company = ''
			if div_company:
				job_company = div_company.text.strip()

			div_location = div.find("div", attrs={"class": "job_location"})
			job_location = ''
			if div_location:
				job_location = div_location.text.strip()

			div_time = div.find("div", attrs={"class": "job_time"})
			if div_time:
				time = div_time.text.strip().split(' ')

				if time[1] in ['days', 'day']:
					online = time[0]
				elif time[1] in ['months']:
					online = int(time[0]) * 30
				elif time[0] == 'about' and time[2] == 'month':
					online = int(time[1]) * 30
				elif time[1] in ['hours']:
					online = float(time[0])/24.0
				else:
					online = div_time.text.strip()

			if job_title and online and job_company and job_location and float(online) < self._max_days:
				jobs.append([webpage, job_title, job_location, job_company, str(online), link])

		return jobs


	def start_crawling(self):
		print("Start %s..." % __name__)
		return super(TheLocalCrawler, self).start_crawling()


	if __name__ == "__main__":
		with TheLocalCrawler() as o:
			o.start_crawling()
			print("TheLocal done!")
