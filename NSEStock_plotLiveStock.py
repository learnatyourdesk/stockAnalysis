import sys
import time
import random
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.animation as animation

sp = []
sp_tmp = []

fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

x_axis = []
c = 0

max_steps = 100

def fetch_NSE_stock_price(stock_code):
    
    print ("Fetching details..")
    stock_url  = 'https://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol='+str(stock_code)
    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'}
    response = requests.get(stock_url, headers=headers)

    print(response)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_array = soup.find(id='responseDiv').getText().strip().split(":")
    for item in data_array:
        if 'lastPrice' in item:
            index = data_array.index(item)+1
            latestPrice=data_array[index].split('"')[1]
            return float(latestPrice.replace(',',''))
    
def plotGraph(i):
   
    global sp_tmp
    global c

    #rnd = random.randint(5,10)
    nse_sp = fetch_NSE_stock_price(stock_code) 
    sp_tmp.append(nse_sp)
    
    c = c +1

    if c <= max_steps:
        x_axis.append(c)
    
    if len(sp_tmp) > max_steps:
        sp = sp_tmp[1:max_steps+1]
    else:
        sp = sp_tmp
    
    sp_tmp = sp
    
    print ("length = "+str(len(sp)))
    print ("length = "+str(len(x_axis)))
    print(sp)
    print(x_axis)

    ax1.clear()
    plt.grid(which='major', linestyle='-', linewidth='0.5', color='red')
    plt.grid(which='minor', linestyle=':', linewidth='0.5', color='black')

    ax1.plot(x_axis,sp)



### MAIN ####

stock_code = sys.argv[1]

ani = animation.FuncAnimation(fig, plotGraph, interval=1000)
plt.show()
