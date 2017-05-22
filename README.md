# Jobs-crawler
Simple website crawler in Python, that searches for new job ads

## Pre-requisites

To run the program the following modules have to be installed first:

	- python-requests
	- python-dateutil
    - python-sqlite


## Content

Currently supported websites:

  - The Local 
  - Neuvoo
  - Monster
  - Arbetsförmedlingen

NOTE: Neuvoo uses an API that only allows a maximum of 25 results to be retrieved!<br/>
NOTE 2: The Local is using some AJAX call for the reload of more than 25 results which is currently not implemented,
so here also only the 25 first results will be retrieved


Found jobs will be saved to a SQLite database and new jobs (that are not yet in the database),
will be saved to a text file *new_jobs.txt*, which is either created or updated in case it exists already.

In the file *libs/Jobs_Crawler.py* the search parameters and the location can be specified!

