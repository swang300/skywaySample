import pyarrow.parquet as parquet
import pandas
import duckdb
from flask import Flask
from flask import request

app = Flask(__name__)
con = duckdb.connect(database = "my-db.duckdb", read_only = False)

@app.route("/loadData")
def loadData():
  con.sql("drop table if exists usage")
  con.sql("create table usage as from 'Oct2018-WorkshopCUR-00001.snappy.parquet'")
  return 'Data loaded successfully', 200
  
@app.route("/services")
def services():
  result = con.sql("select distinct product_servicecode from Usage where line_item_line_item_type = 'Usage'").df()
  
  retVal = result['product_servicecode'].tolist()
  print(retVal)
  return retVal, 200

  
def unblended(service):
  if (service != 'ALL'):
    queryText = "select sum(line_item_unblended_cost) from Usage where product_servicecode = '"+service+"' and line_item_line_item_type = 'Usage'"
  else:
    queryText = "select sum(line_item_unblended_cost) from Usage where line_item_line_item_type = 'Usage'"
  result = con.sql(queryText).fetchone()
  return result[0]

@app.route("/unblended")
def unblendedEndpoint():
  service = request.args.get('service', default = 'ALL', type=str)
  return str(unblended(service)), 200

def discounted(service):
  if (service != 'ALL'):
    queryText = "select product_servicecode,line_item_unblended_cost from Usage where product_servicecode = '"+service+"' and line_item_line_item_type = 'Usage'"
  else:
    queryText = "select product_servicecode,line_item_unblended_cost from Usage where line_item_line_item_type = 'Usage'"
  result = con.sql(queryText).fetchall()
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
  
@app.route("/discounted")
def discountedEndpoint():
  service = request.args.get('service', default = 'ALL', type=str)
  return str(discounted(service)), 200
  
if __name__ == "__main__":
  app.run()