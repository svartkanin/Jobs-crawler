import socket
from libs.monster_crawler import MonsterCrawler
from libs.neuvoo_crawler import NeuvooCrawler
from libs.arbetsfoermedlingen_crawler import ArbetsfoermedlingenCrawler
from libs.thelocal_crawler import TheLocalCrawler
import gi

gi.require_version('Notify', '0.7')
from gi.repository import Notify


def _check_internet_connection():
	host = "8.8.8.8"
	port = 53
	timeout = 3

	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except Exception as ex:
		print("No internet connection available!")
		return False


def __remove_duplicates(data):
	tmp_list = []
	for job in data:
		if not any(job[1:3] == entry[1:3] for entry in tmp_list):
			tmp_list.append(job)

	return tmp_list


def __pretty_print(data):
	len_columns = [0] * len(data[0])

	# determine max length for each column in the output file
	for i in range(0, len(data[0])):
		len_columns[i] = max([len(" ".join(column[i].split())) for column in data])

	text = ''
	for job in data:
		line = ''
		i = 0
		for elem in job:
			tmp = " ".join(elem.split())
			line += tmp.ljust(len_columns[i] + 2)
			i += 1

		text += line + '\n'

	return text + '\r'


def __notify_new_jobs():
	Notify.init("New jobs")

	summary = "New Jobs"
	body = "new jobs available"
	notification = Notify.Notification.new(
		summary,
		body,  # Optional
		"dialog-information"
	)

	notification.set_urgency(2)  # Highest priority
	notification.show()


if __name__ == "__main__":
	if _check_internet_connection():
		new_jobs = []

		with NeuvooCrawler() as n:
			new_jobs.extend(n.start_crawling())

		print('')
		with MonsterCrawler() as m:
			new_jobs.extend(m.start_crawling())

		print('')
		with ArbetsfoermedlingenCrawler() as a:
			new_jobs.extend(a.start_crawling())

		print('')
		with TheLocalCrawler() as t:
			new_jobs.extend(t.start_crawling())

		if new_jobs:
			new_jobs = __remove_duplicates(new_jobs)
			new_jobs = sorted(new_jobs, key=lambda x: float(x[4]))
			pretty_jobs = __pretty_print(new_jobs)
			__notify_new_jobs()

			with open("new_jobs.txt", 'a') as fp:
				fp.write(pretty_jobs)

	print('Done')
