# Report for news database

This is a reporting tool for the newspaper that extracts insights about the site's readers preferences.

This report answers three questions:

1.  What are the most popular three articles of all time?
2.  Who are the most popular article authors of all time?
3.  On which days did more than 1% of requests lead to errors?

### Requirements

To run this report, the folowing software and libraries are necessary:
* PostgreSQL - installation instructions [here](https://www.postgresql.org/docs/9.3/installation.html)
* Python 2.7 - installation instructions [here](https://www.python.org/downloads/)
* Additional Python libraries:
    * psycopg2 - installation instructions [here](https://pypi.org/project/psycopg2/)
    * pandas - installation instructions [here](https://pypi.org/project/pandas/)

### How to run this report

It is necessary to download the database with the historical information. Access [this link](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip) to download the zipped database, then unzip it and save it in the same directory of the application.

And to import the database, in the command prompt, type the following command:

```sh
$ psql -d news -f newsdata.sql
```
To run the report, you should execute the following command in the command prompt:

```sh
$ python report.py
```
The report will show the results in the command window.

#### Author
Cristiana Parada - cris@best.com.br
