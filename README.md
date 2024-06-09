Requirements:

python, git (optional), browser

installation (recommended):

Download or clone git project, and start a shell in the directory

#recommended venv to separate packages from other projects

python -m venv

#activate.ps1 for powershell, activate.bat for windows terminal

venv\Scripts\activate

pip install -r requirements.txt

python .\skywaySample.py

#Load the data, only required once

browse to: http://localhost:5000/loadData

#the actual html page

browse to: http://localhost:5000/static/discount.html

The service type ALL is for the entire bill.

---------------------------
Answers to questions:
1) How long did this take you?  Roughly what was the breakdown of that time?

  ~2 hours on the server

  ~1.5 hours on the html page

2) What’s your prior experience like with the language you chose?

  I've done this exact type of programmatic ETL quite a few times with Python and Flask.

3) Did you make any assumptions about the project and/or its requirements that we should know?

  There are roughly 1.5k lines with no service code, it's not a lot in terms of the charge $31 (I think) but it warrants invstigation.  I've simply treated those lines as just another service with name ""

  I tied all 3 API calls to one single button, but they can be called with separate buttons.

4) If you were building this over again, is there anything you’d change?

  I spent about 45 minutes or so on the html page setting up react, realized that I have another hour or 2 of this setup, and abandoned it for just a straightforward async javascript implementation.

  I'd probably look a little harder at using DuckDB.  As it is, sqlite is pretty pointless other than to demonstrate that I know how to use sqlalchemy. It's probably slower than loading the parquet into memory and dealing with everything as dataframes.

5) If you were making a production version of this (and feel free to make assumptions about what that looks like), what would you change?

  Keep unused Data, we probably need it.

  Implement a real datatore.

  Investigate whether we can drop raw SQL in DuckDB and go with typesafe/object oriented queries.  Raw SQL is not very easy to maintain.

  Do more calculations in the datastore.

  Calculation caching.  (right now, the discount rate runs the unblended and the discounted costs again, there's really no reason to do this other than faster time to market.)

  Provide time-series values.

  Multi-tenancy

  Get a prettier UI, and more functional.

7) If you had to do this work on a dataset that was 100x the size, what would you change?

  For this specifc use case, 100x doesn't matter too much. After filtering, it's not a lot of data.  Keeping unused data would require keeping the data in a real DB, especially at 100x.
  
  We'd probably want to move the discounted cost sql into the DB (there's a case statement in SQL, raw SQL is also a bit harder to maintain.)
  
  In-memory caching of the unblended and discounted costs should start to happen.

  At 100x more than that, you would want to look into pre-caching of calculations, nightly batch processing, and a job submittal system to cache un-cached calculations.
  
7) Were there any parts of the instructions that were confusing or could be made more clear?  We’re always looking to improve this challenge!

  While working on the UI, I found it much easier to change the implementation of the discount ratio to accept a service type, and to add the custom Service type ALL to the other two calls.  This made the UI much easier to deal with and didn't change the requested functionality much.

