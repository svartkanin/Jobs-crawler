import sys
import sqlite3
import requests
import urllib2


class Crawler(object):

	search_location = ["Liverpool", "England"]
	search_parameters = [['software', 'developer]]

	def __init__(self, urls, mode="HTML"):
		self.__urls = urls
		self.__jobs_container = []
		self.__new_jobs_container = []
		self.__processed_urls = []
		self.__mode = mode
		# only ads up till 5 days should be shown
		self._max_days = 5
		self._db_name = 'jobs.db'

		self._jobs_counter = 0

		reload(sys)
		sys.setdefaultencoding('utf8')

		self.__db_conn = sqlite3.connect(self._db_name)


	def __enter__(self):
		return self


	def __exit__(self, exc_type, exc_value, traceback):
		self.__db_conn.close()


	def find_jobs_string(self, source_code):
		pass


	def extract_jobs_from_source(self, json_data):
		pass


	def check_pagination(self, url, source_code):
		return []


	def __get_html_pagesource(self, url):
		response = urllib2.urlopen(url, timeout=5)
		page_source = response.read()

		return page_source


	def __get_json(self, url):
		headers = {'Accept-Language': 'en'}
		r = requests.get(url, headers=headers)
		if r:
			return r.json()
		else:
			return ''


	def __check_pagination(self, url, base_url, source_code):
		pages = self.check_pagination(url, source_code)

		if len(pages) > 1:
			for p in pages:
				page_num = p[2]
				replace_string = p[0]
				replace_with = p[1]

				if replace_string:
					tmp = base_url.split(replace_string)
					new_url = tmp[0] + replace_with + tmp[1]
				else:
					new_url = base_url + replace_with

				if page_num != 1 and not any(page_num == i[1] for i in self.__processed_urls):
					self.__handle_url(new_url, base_url, page_num)


	def __handle_url(self, url, base_url, page):
		print('\t\tProcessing page %d: %s' % (page, url,))

		if page == 1:
			self.__processed_urls = []

		self.__processed_urls.append([url, page])

		if self.__mode == "JSON":
			ret = self.__get_json(url)
		else:
			ret = self.__get_html_pagesource(url)

		if ret:
			jobs = self.extract_jobs_from_source(ret)

			self._jobs_counter += len(jobs)

			self.__jobs_container.extend(jobs)

		if self.__mode != "JSON" and self.__mode != "RELOAD":
			self.__check_pagination(url, base_url, ret)

		return ret


	def __check_new_jobs(self):
		cur = self.__db_conn.cursor()
		select = "SELECT * FROM jobs WHERE webpage = ? AND job_title = ? AND job_location = ? AND job_company = ?"

		for job in self.__jobs_container:
			t = (job[0], job[1], job[2], job[3])

			# For debugging only
			# s = select
			# if len(t) > 0:
			#     # generates SELECT quote(?), quote(?), ...
			#     cur.execute("SELECT " + ", ".join(["quote(?)" for i in t]), t)
			#     quoted_values = cur.fetchone()
			#     for quoted_value in quoted_values:
			#         s = s.replace('?', quoted_value, 1)
			# print "SQL command: " + s
			# cur.execute(select, t)

			cur.execute(select, t)

			ret = cur.fetchone()
			if not ret:
				self.__new_jobs_container.append(job)


	def __create_db_tables(self):
		cur = self.__db_conn.cursor()
		cur.execute("""CREATE TABLE IF NOT EXISTS jobs (webpage text, job_title text, job_location text, job_company text, online real, link text,
						UNIQUE(webpage, job_title, job_location, job_company)
						)""")

		self.__db_conn.commit()


	def __write_to_db(self, jobs):
		cur = self.__db_conn.cursor()
		for job in jobs:
			cur.execute('INSERT OR IGNORE INTO jobs values (?,?,?,?,?,?)', job)

		self.__db_conn.commit()


	def start_crawling(self):
		self.__create_db_tables()
		ret = -1

		for key, values in self.__urls.iteritems():
			print("\tSearch value '" + key + "':")
			self._jobs_counter = 0
			for value in values:
				ret = self.__handle_url(value, value, page=1)
				print("\t\tFound " + str(self._jobs_counter) + " jobs")

		if ret == -1:
			return

		self.__check_new_jobs()

		if self.__jobs_container:
			self.__write_to_db(self.__jobs_container)

		return self.__new_jobs_container
