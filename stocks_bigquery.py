from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
import requests, sqlite3, os, pandas

url_today = datetime.now().strftime('%Y%m%d')
twse_today = f"{datetime.now().year-1911}/{datetime.now().strftime('%m/%d')}"
stocks = ['2330', '0050', '2409']
    
combined = []
for stock_no in stocks:
    response = requests.get(f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={url_today}&stockNo={stock_no}')
    response_data = response.json()['data']
 
    result = [data for index, data in enumerate(response_data) if twse_today in response_data[index]]
 
    if result:
        result[0].insert(0, stock_no)
        combined.append(result[0])

df = pandas.DataFrame(combined,columns=['stock_no', 'traded_date', 'traded_shares', 'traded_price','opening_price', 'high_price', 'low_price', 'closing_price', 'gross_spread', 'trading_volume'])
    #使用google service_account來讀取credentials
credentials = service_account.Credentials.from_service_account_file('stocks-bigquery-forresttest-5b337d75564b.json')
client = bigquery.Client(credentials=credentials)
table_id = "stocks-bigquery-forresttest.stocks.daily_price"
    # job是執行的物件，result是執行method
job = client.load_table_from_dataframe(df,table_id)
job.result()
table = client.get_table(table_id)
print(f'已存入{table.num_rows}筆資料到{table_id}')