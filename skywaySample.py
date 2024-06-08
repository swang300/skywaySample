import pyarrow.parquet as parquet
import pandas
import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from flask import Flask
from flask import request

app = Flask(__name__)
engine = create_engine('sqlite:///usage.sqlite', echo=False)

@app.route("/loadData")
def loadData():
  table = parquet.read_table('Oct2018-WorkshopCUR-00001.snappy.parquet')
  df = table.to_pandas()
  usageOnly = df[df['line_item_line_item_type'] == 'Usage']
  filtered = usageOnly[['line_item_unblended_cost','product_servicecode']]
  Base = declarative_base()
  metadata = MetaData()
  metadata.reflect(bind=engine)
  table = metadata.tables['Usage']
  if table is not None:
    Base.metadata.drop_all(engine, [table], checkfirst=True)
  filtered.to_sql('Usage', con=engine, if_exists='append')
  return 'Data loaded successfully', 200
  
@app.route("/services")
def services():
  with engine.connect() as con:
    sql = text('select distinct product_servicecode from Usage;')
    result = con.execute(sql).fetchall()
  retVal = []
  for row in result:
    retVal.append(row[0]);
  return retVal, 200

def unblended(service):
  if (service != 'ALL'):
    queryText = "select line_item_unblended_cost from Usage where product_servicecode = '"+service+"';"
  else:
    queryText = 'select line_item_unblended_cost from Usage;'
  with engine.connect() as con:
    sql = text(queryText)
    result = con.execute(sql).fetchall()
  retVal = 0
  for row in result:
    retVal+=row[0];
  return retVal

@app.route("/unblended")
def unblendedEndpoint():
  service = request.args.get('service', default = 'ALL', type=str)
  return str(unblended(service)), 200
  
def discounted(service):
  if (service != 'ALL'):
    queryText = "select product_servicecode,line_item_unblended_cost from Usage where product_servicecode = '"+service+"';"
  else:
    queryText = 'select product_servicecode,line_item_unblended_cost from Usage;'
  with engine.connect() as con:
    sql = text(queryText)
    result = con.execute(sql).fetchall()
  retVal = 0
  for row in result:
    match row[0]:
      case 'AmazonS3':
        ratio = 0.88
      case 'AmazonEC2':
        ratio = 0.5
      case 'AWSDataTransfer':
        ratio = 0.7
      case 'AWSGlue':
        ratio = 0.95
      case 'AmazonGuardDuty':
        ratio = 0.25
      case _:
        ratio = 1
    retVal+=row[1]*ratio;
  return retVal
  
@app.route("/discounted")
def discountedEndpoint():
  service = request.args.get('service', default = 'ALL', type=str)
  return str(discounted(service)), 200
    
@app.route("/discountRate")
def discountRateEndpoint():
  service = request.args.get('service', default = 'ALL', type=str)
  unblendedSum = unblended(service)
  discountedSum = discounted(service)
  
  if (unblendedSum != 0):
    rate = 1 - (discountedSum/unblendedSum)
  else:
    rate = 1
  return str(rate), 200
  
if __name__ == "__main__":
  app.run()