# ao3mine

AO3 mine is a scraper for ao3 query searches, collecting metadata and storing it in mySQL, and notebooks for analysis of the databases collected. 

This project uses pandas, sqlite3, beautifulsoup. The code is not yet published as a library but specific functions in ao3.py can be accessed in notebooks with the suitable priming cell (see Demo notebooks).

The OTW asks that scrapers send request with 5 second delays and to avoid collecting data on weekends, when the site has the most user traffic. Please respect their request.