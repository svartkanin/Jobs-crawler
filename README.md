# Jobs crawler

A simple crawler for job ads on different websites.

## Supported websites

Currently the following websites are supported:

- Neuvoo
- Monster

## Configuration

The configuration for search terms, location and which websites to include can be set in the `config.json` file. An example of the configuration is shown below:

```
{
  "search_terms": [
    "Python developer"
  ],
  "country": "Sweden",
  "location": "Stockholm",
  "websites": [
    "Monster",
    "Neuvoo"
  ],
  "output_file": "new_jobs.txt"
}
```

**NOTE**  
Any website does only support certain countries. For a full list of supported countries for each site view the mapping files `crawler/monster_mapping.json` and `crawler/neuvoo_mappings.json`. If a country is specified that is supported for one website but not the other, the crwaler will only crawl the supported one.

## Required packages

The crawler requires some dependencies to be installed, just run the following command:
```
pip install -r requirements.txt
```

### Run

The application was tested with `Python 3.7+` so make sure you're using that version or higher.
To execute the crawler run:
```
python crawl.py
```

### Output

The crawled data is stored in a local `sqlite3` database file. All newly received job ads are also written to an **output file** with the name specified in the configuration file, however, only new ads will be outputed to that file.
