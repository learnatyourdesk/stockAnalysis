import pandas as pd
import sys
import requests
from bs4 import BeautifulSoup
import re
import os

def fetch_NSE_stock_price(stock_code):
    
    stock_url  = 'https://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol='+str(stock_code)
    #print(stock_url)
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
    response = requests.get(stock_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_array = soup.find(id='responseDiv').getText().strip().split(":")
    
    for item in data_array:
        if 'lastPrice' in item:
            index = data_array.index(item)+1
            latestPrice=data_array[index].split('"')[1]
            lp =  float(latestPrice.replace(',',''))
        elif 'closePrice' in item:
            index = data_array.index(item)+1
            closePrice=data_array[index].split('"')[1]
            cp =  float(closePrice.replace(',',''))
        elif 'open' in item:
            index = data_array.index(item)+1
            openPrice=data_array[index].split('"')[1]
            op =  float(openPrice.replace(',',''))
        elif 'dayLow' in item:
            index = data_array.index(item)+1
            dayLow=data_array[index].split('"')[1]
            dl =  float(dayLow.replace(',',''))
        elif 'dayHigh' in item:
            index = data_array.index(item)+1
            dayHigh=data_array[index].split('"')[1]
            dh =  float(dayHigh.replace(',',''))
    return op,lp,dh, dl,cp       

nifty50_url = 'https://www1.nseindia.com/content/indices/ind_nifty50list.csv'
df_n50 = pd.read_csv(nifty50_url)

regexp = re.compile('&')

OP  = []
LP  = []
DHP = []
DLP = []
CP  = []


while True:
   try:
      for index, row in df_n50.iterrows():
         stock_code = row['Symbol']
         if(regexp.search(stock_code) != None):
            stock_code = stock_code.replace('&','%26')
         
         oPrice,lPrice,dhPrice, dlPrice,cPrice = fetch_NSE_stock_price(stock_code)
         OP.append(str(oPrice))
         LP.append(str(lPrice))
         DHP.append(str(dhPrice))
         DLP.append(str(dlPrice))
         CP.append(str(cPrice))

      os.system('cls')
      print("--------------------------------------------------------------------------------------------------------------------------------------------")
      print("|{:50s} | {:20s} | {:10s} | {:10s} | {:10s} | {:10s} | {:10s}|".format( 'Company Name','Symbol','openPrice','lastPrice','dayHigh','dayLow','closePrice'))
      print("--------------------------------------------------------------------------------------------------------------------------------------------")


      for index, row in df_n50.iterrows():
         stock_code = row['Symbol']
         
         print("|{:50s} | {:20s} | {:10s} |{:10s} | {:10s} | {:10s} | {:10s} |".format(str(row['Company Name']), row['Symbol'], OP[index].rjust(10), LP[index].rjust(10), DHP[index].rjust(10), DLP[index].rjust(10), CP[index].rjust(10)))
         
      print("--------------------------------------------------------------------------------------------------------------------------------------------")

   except KeyboardInterrupt:
        sys.exit()
