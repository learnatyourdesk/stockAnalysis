## This is recomanded to watch part1 and part2 of of same series
## Part1: https://www.youtube.com/watch?v=Tke9SzbAqHc&t=1092s
## Part2: https://www.youtube.com/watch?v=tm8RiH72MLA&t=1602s

import requests
import json
import pandas as pd
import getopt
import sys

oc_data = {}

# List of fields not required in out while displaying option chain date
keys_to_exclude = [
                    'pchangeinOpenInterest', 
                    'totalBuyQuantity', 
                    'totalSellQuantity', 
                    'underlyingValue',
                    'expiryDate',
                    'underlying',
                    'identifier',
                    'pChange'
]

#############################################################
## Funtion to restric decimal value to n place
## In this example decimle value is restricted
## to only 2 places
#############################################################
def set_decimal(x):
    return ('%.2f' % x).rstrip('0').rstrip('.')


#############################################################
## Function to scrap data from NSE website and create
## json object so that it can be processed further easly
#############################################################
def create_json_object(u,h,t_o):
    response = requests.get(u, headers=h, timeout=t_o)

    response_text=response.text
    jo = json.loads(response_text)

    return jo


#############################################################
## Function to remove unwanted content
#############################################################
def format_oc_data(e_dt, data):
    oc_d = {}
    for ed in e_dt:
        oc_d[ed]={"CE":[], "PE":[]}
        for di in range(len(data)):
            
            if data[di]['expiryDate'] == ed:
                if 'CE' in data[di].keys() and data[di]['CE']['expiryDate'] == ed:                
                    oc_d[ed]["CE"].append(data[di]['CE'])
                else:
                    oc_d[ed]["CE"].append('-')

                if 'PE' in data[di].keys() and data[di]['PE']['expiryDate'] == ed:
                    oc_d[ed]["PE"].append(data[di]['PE'])
                    
                else:
                    oc_d[ed]["PE"].append('-')
    return oc_d


#############################################################
## Function to format and create final list of Option Chain
## data which is similar to NSE website
#############################################################
def create_final_OC_matrix(CE, PE):
    l_OC = []
    for i in range(len(CE)):
        if CE[i] != '-':
            for key in keys_to_exclude:
                del CE[i][key]

        if PE[i] != '-':
            for key in keys_to_exclude:
                del PE[i][key]

    for i in range(len(CE)):
        l_CE=[]
        l_PE=[]

        if CE[i] != '-':
            sp = CE[i]['strikePrice']
            l_CE =  [  
                        CE[i]['openInterest'], 
                        CE[i]['changeinOpenInterest'] , 
                        CE[i]['totalTradedVolume'] , 
                        CE[i]['impliedVolatility'] , 
                        CE[i]['lastPrice'] , 
                        set_decimal(CE[i]['change']), 
                        CE[i]['bidQty']   , 
                        CE[i]['bidprice'] , 
                        CE[i]['askPrice'] ,
                        CE[i]['askQty'] , 
                        CE[i]['strikePrice']
                    ]
        else:
            sp = PE[i]['strikePrice']
            l_CE= list(['-','-','-','-','-','-','-','-','-','-',sp])

        if PE[i] != '-':
            l_PE =  [
                        PE[i]['bidQty']   ,
                        PE[i]['bidprice'] ,
                        PE[i]['askPrice'] ,
                        PE[i]['askQty'] , 
                        set_decimal(PE[i]['change']),
                        PE[i]['lastPrice'] ,
                        PE[i]['impliedVolatility'] ,
                        PE[i]['totalTradedVolume'] ,
                        PE[i]['changeinOpenInterest'] ,
                        PE[i]['openInterest']
            ] 

        else:
            l_PE = list(['-','-','-','-','-','-','-','-','-','-'])
        
        
        l_OC_t = l_CE + l_PE
        l_OC_t[:] = [x if x != 0 else '-' for x in l_OC_t]

        l_OC.append(l_OC_t)

    return l_OC


#############################################################
## Main function
#############################################################
if __name__ == '__main__':
    try:
        list_expiry_dates = False
        ed_by_index = False
        i_dt = None
        EXPIRY_DATE   = None
        SYMBOL = 'NIFTY'
        url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
               
        headers={'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}

        argv = sys.argv[1:]
        if len(argv) == 0:
            raise Exception

        opts, args = getopt.getopt(argv, "ed:i:s:")
        
        for opt, arg in opts:
            if opt in ['-e']:
                list_expiry_dates = True

            elif opt in ['-d']:
                EXPIRY_DATE = arg

            elif opt in ['-i']:
                ed_by_index = True
                i_dt = int(arg)

            else:    
                print("Error: Invalid arguments")
    
        print(url)
        json_object = create_json_object(url,headers,10)
        data = json_object['records']['data']
        e_date=json_object['records']['expiryDates']

        if list_expiry_dates:
            for dt in e_date:
                print('(', e_date.index(dt), ') ', dt)            
        else:
            if ed_by_index:
                EXPIRY_DATE = e_date[i_dt]
            
            oc_data = format_oc_data(e_date, data)
            oc_data_dt=oc_data[EXPIRY_DATE]

            call_data=list(oc_data_dt['CE'])
            put_data=list(oc_data_dt['PE'])

            l_final_oc_data= create_final_OC_matrix(call_data, put_data)

            pd.set_option('display.max_rows', None)
        
            df = pd.DataFrame(l_final_oc_data)

            OC_col = ['c_OI', 'c_CHNG_IN_OI', 'c_VOLUME', 'c_IV', 'c_LTP', 'c_CHNG', 'c_BID_QTY', 'c_BID', 'c_ASK', 'c_ASK_QTY',  'STRIKE', 'p_BID_QTY', 'p_BID', 'p_ASK', 'p_ASK_QTY',  'p_CHNG', 'p_LTP', 'p_IV', 'p_VOLUME', 'p_CHNG_IN_OI', 'p_OI'] 

            df.columns = OC_col


            print('')
            print('Symbol     : ', SYMBOL)
            print('Expiry Date: ', EXPIRY_DATE)
            print('-------------------------')                                        
            print(df)

    except:
        print("Please enter a valid option\n")
        print('To list expiry dates')
        print("  usage: layd_OC_NSE_Part3.py -e\n")
        print('To list option chain data for given expiry date. Do not provide date in quote.')
        print("  usage: layd_OC_NSE_Part3.py -d <expiry data>")
        print("  usage: layd_OC_NSE_Part3.py -i <expiry date index listed during -e option>")
