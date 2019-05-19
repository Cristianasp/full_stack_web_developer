#!/usr/bin/env python

###############################################################################
# Udacity Nanodegree FullStack Web developer
# Project 1
# author: Cristiana Parada cris@best.com.br
###############################################################################

###############################################################################
# Importing libraries
###############################################################################
import psycopg2
import datetime as dt
import pandas as pd

###############################################################################
# Defining constants
###############################################################################
DBNAME = "news"

###############################################################################
# SQL CODE for each question
###############################################################################

QUESTION_1 = '''
1. What are the most popular three articles of all time?
'''
# Which articles have been accessed the most?
# Present this information as a sorted list with the most popular article at
# the top

SQL_1 = '''
SELECT ARTICLES.TITLE, COUNT(LOG.ID) AS QTDE
        FROM ARTICLES LEFT JOIN LOG
        ON CONCAT('/article/', ARTICLES.SLUG) = LOG.PATH
        GROUP BY ARTICLES.TITLE
        ORDER BY QTDE DESC
        LIMIT 3
;
'''

QUESTION_2 = '''
2. Who are the most popular article authors of all time?
'''
# That is, when you sum up all of the articles each author has written, which
# authors get the most page views?
# Present this as a sorted list with the most popular author at the top

SQL_2 = '''
SELECT AUTHORS.NAME, SUM(ARTICLES_COUNT.QTDE) AS TOTAL
  FROM
        (SELECT ARTICLES.TITLE, ARTICLES.AUTHOR, COUNT(LOG.ID) AS QTDE
        FROM ARTICLES LEFT JOIN LOG
        ON CONCAT('/article/', ARTICLES.SLUG) = LOG.PATH
        GROUP BY ARTICLES.TITLE, ARTICLES.AUTHOR
        ORDER BY QTDE DESC) AS ARTICLES_COUNT
  INNER JOIN AUTHORS
  ON AUTHORS.ID = ARTICLES_COUNT.AUTHOR
  GROUP BY AUTHORS.ID
  ORDER BY TOTAL DESC
;
'''

QUESTION_3 = '''
3. On which days did more than 1% of requests lead to errors?
'''
# The log table includes a column status that indicates the HTTP status code
# that the news site sent to the user's browser.

SQL_3 = '''
SELECT TO_CHAR(S400.DIA,'YYYY-MM-DD'), S400.QTDE, S200.QTDE ,
               to_char( S400.QTDE/ (CAST(S200.QTDE as float) + S400.QTDE) * 100,'999D999%')
               AS PERC
FROM
    (SELECT TIME::DATE AS DIA, STATUS, COUNT(*) AS QTDE
    FROM LOG WHERE STATUS='404 NOT FOUND'
    GROUP BY DIA, STATUS) AS S400
    INNER JOIN
        (SELECT TIME::DATE AS DIA, STATUS, COUNT(*) AS QTDE
        FROM LOG WHERE STATUS='200 OK'
        GROUP BY DIA, STATUS) AS S200
    ON S400.DIA = S200.DIA
    WHERE  S400.QTDE/ CAST(S200.QTDE AS FLOAT) > 0.01
;

'''
###############################################################################


def RunQuery(SQLCODE):
    '''
    Function that runs the SQL code in the database and returns the results
    input: string with SQL code
    return: fetched rows from the database or empty if fails
    '''
    try:
        db = psycopg2.connect(database=DBNAME)
        c = db.cursor()
        c.execute(SQLCODE)
        rows = c.fetchall()
        db.close()
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

###############################################################################


if __name__ == '__main__':

    # Print Header of Report
    print("Reporting for news database (processed on " +
          str(dt.datetime.now().strftime("%Y-%m-%d %H:%M"))+")")

    print(QUESTION_1)
    result = pd.DataFrame(RunQuery(SQL_1), columns=["Authors", "Page Views"])
    print(result.to_string(index=False))

    print(QUESTION_2)
    result = pd.DataFrame(RunQuery(SQL_2), columns=["Author", "Page Views"])
    print(result.to_string(index=False))

    print(QUESTION_3)
    result = pd.DataFrame(RunQuery(SQL_3),
                          columns=["Date", "Errors", "Success", "Percentage"])
    print(result.to_string(index=False))
