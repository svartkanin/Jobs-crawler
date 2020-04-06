import sqlite3
import logging
import urllib.request

from datetime import datetime

logger = logging.getLogger(__name__)


class JobAd():
    def __init__(self, webpage):
        self._title = None
        self._location = None
        self._company = None
        self._posted = None
        self._link = None
        self._webpage = webpage

    @property
    def title(self):
        return self._title

    @property
    def location(self):
        return self._location

    @property
    def company(self):
        return self._company

    @property
    def posted(self):
        return self._posted

    @property
    def link(self):
        return self._link

    @property
    def webpage(self):
        return self._webpage

    @title.setter
    def title(self, title):
        self._title = title

    @location.setter
    def location(self, l):
        self._location = l

    @company.setter
    def company(self, c):
        self._company = c

    @posted.setter
    def posted(self, o):
        self._posted = o

    @link.setter
    def link(self, l):
        self._link = l

    @webpage.setter
    def webpage(self, w):
        self._webpage = w

    def prepare_insert(self):
        """
        Prepare the job datastructure to align with the
        database fields

        Returns:
            list: Fields to be stored in the database
        """
        return [
            self._webpage, self._title, self._location, self._company,
            self._link
        ]

    def prepare_output(self):
        """
        Prepare the job datastructure for the output file

        Returns:
            str: String representation of the job ad
        """
        return (
            f'{self._webpage} | {self._title} | {self._location} | {self._company} | {self._link}'
        )


class Crawler(object):
    def __init__(self, config_data):
        self._config_data = config_data
        self._query_urls = None
        self._job_ads = []
        self._job_ads_new = []

        self._db = sqlite3.connect('job_ads.sqlite')
        self._init_db()

    def _init_db(self):
        """
        Initialize the database and create tables if they don't
        exist yet
        """
        cur = self._db.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS job_ads (
                webpage text,
                title text,
                location text,
                company text,
                link text
            )
        """)

        self._db.commit()

    def setup(self, web_obj):
        """
        Prepare the crawler with a new webpage crawler

        Args:
            web_obj (obj): Webpage crawler to be used for crawling
        """
        self._web_obj = web_obj
        self._query_urls = self._web_obj.prepare_urls()
  
    def fetch_html_listings(self):
        """
        Start fetching html listing for a specific webpage craler
        """
        webpage = self._web_obj.__class__.__name__
        logger.info(f'{webpage} - Start fetching html listings...')

        for count, url in enumerate(self._query_urls):
            logger.info(f'{webpage} - {count+1}/{len(self._query_urls)} {url}')

            response = urllib.request.urlopen(url)
            page_source = response.read()

            ads = self._web_obj.parse_data(page_source)
            self._job_ads.extend(ads)

    def save_job_ads(self):
        """
        Save found job ads to the database
        """
        cur = self._db.cursor()

        for job in self._job_ads:
            cur.execute('SELECT count(*) FROM job_ads WHERE link=?',
                        [job.link])

            if cur.fetchone()[0] > 0:
                self._job_ads_new.append(job)
            else:
                cur.execute(
                    """
                    INSERT INTO job_ads (
                        webpage,
                        title,
                        location,
                        company,
                        link
                    ) values (
                        ?,?,?,?,?
                    )""", job.prepare_insert())

        self._db.commit()
        self._job_ads = []

    def output_new_jobs(self):
        """
        Output new job ads to the output file
        """
        output_file = self._config_data['output_file']
        logger.info(f'Writing new jobs to "{output_file}"')

        with open(output_file, 'r+') as fp:
            file_data = fp.read()

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            output_text = f'[{timestamp}]\n'

            for job in self._job_ads_new:
                output_text += job.prepare_output() + '\n'

            # output the new jobs to the top of the file
            fp.seek(0)
            fp.write(f'{output_text}\n\n{file_data}')
