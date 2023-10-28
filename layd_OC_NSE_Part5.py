## This is recomanded to watch part1 and part2 of of same series
## Part1: https://www.youtube.com/watch?v=Tke9SzbAqHc&t=1092s
## Part2: https://www.youtube.com/watch?v=tm8RiH72MLA&t=1602s

import os
import json
import time
import requests
import pandas as pd
from tabulate import tabulate
from msvcrt import getch,kbhit

#############################################################
## List of key codes
## This list is used in function find_2dl_index to check
## which key is pressed
#############################################################
keys_mapping =  [
                    [72, 'UP'],
                    [80, 'DOWN'],
                    [27, 'ESC']
               ]

#############################################################
## Funtion return str value of key pressed based on
## list key+pressed
## 
#############################################################
def find_2dl_index(myList, val):
    for i, x in enumerate(myList):
        if val in x:
            return myList[i][1]

#########################################################################
## List of fields not required in out while displaying option chain date
##
#########################################################################
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
## Function to to return all expiry dates
##  
#############################################################
def create_OC_JSON_object(u, h, t_o):

    inLoop = True
    r = 10
    c = 0

    while inLoop:

        response = requests.get(u, headers=h, timeout=t_o)

        if response.status_code == 200:
            jo = json.loads(response.text)

            return True, jo
        else:
            print('Retry: ', c, ' ', response.status_code)
            c = c +1
            time.sleep(5)

            if c >= r:
                return False, None
            
#############################################################
## Function to to return all expiry dates
##  
#############################################################
def create_edate_data_dict(oc_json_obj):
    
    r_data = oc_json_obj['records']['data']
    e_dt=oc_json_obj['records']['expiryDates']
    
    oc_data = {}
    
    for ed in e_dt:
        
        oc_data[ed]={"CE":[], "PE":[]}
        
        for di in range(len(r_data)):
            if r_data[di]['expiryDate'] == ed:
                if 'CE' in r_data[di].keys() and r_data[di]['CE']['expiryDate'] == ed:                
                    oc_data[ed]["CE"].append(r_data[di]['CE'])
                else:
                    oc_data[ed]["CE"].append('-')

                if 'PE' in r_data[di].keys() and r_data[di]['PE']['expiryDate'] == ed:
                    oc_data[ed]["PE"].append(r_data[di]['PE'])
                else:
                    oc_data[ed]["PE"].append('-')
                                    
    return oc_data
            
#############################################################
## Function to remove unwanted content
#############################################################
def delete_unwanted_fields(oc_full_data):
    
    exp_dates = list(oc_full_data.keys())
    
    for e_dt in exp_dates:

        for i in range(len(oc_full_data[e_dt]['CE'])):
            if oc_full_data[e_dt]['CE'][i] != '-':
                for key in keys_to_exclude:
                    del oc_full_data[e_dt]['CE'][i][key]

            if oc_full_data[e_dt]['PE'][i] != '-':
                for key in keys_to_exclude:
                    del oc_full_data[e_dt]['PE'][i][key]



#############################################################
## Function to format and create final list of Option Chain
## data which is similar to NSE website
#############################################################
def preprate_final_data(r_ce, r_pe):
    l_OC = []

    for i in range(len(r_ce)):
        l_CE=[]
        l_PE=[]

        if r_ce[i] != '-':
            sp = r_ce[i]['strikePrice']
            l_CE =  [  
                        r_ce[i]['openInterest'],        r_ce[i]['changeinOpenInterest'] , 
                        r_ce[i]['totalTradedVolume'],   r_ce[i]['impliedVolatility'] , 
                        r_ce[i]['lastPrice'],           set_decimal(r_ce[i]['change']), 
                        r_ce[i]['bidQty'],              r_ce[i]['bidprice'] , 
                        r_ce[i]['askPrice'],            r_ce[i]['askQty'] , 
                        r_ce[i]['strikePrice']
                    ]
        else:
            sp = r_pe[i]['strikePrice']
            l_CE= list(['-','-','-','-','-','-','-','-','-','-',sp])

        if r_pe[i] != '-':
            l_PE =  [
                        r_pe[i]['bidQty'],              r_pe[i]['bidprice'] ,
                        r_pe[i]['askPrice'],            r_pe[i]['askQty'] , 
                        set_decimal(r_pe[i]['change']), r_pe[i]['lastPrice'] ,
                        r_pe[i]['impliedVolatility'],   r_pe[i]['totalTradedVolume'] ,
                        r_pe[i]['changeinOpenInterest'],r_pe[i]['openInterest']
            ] 

        else:
            l_PE = list(['-','-','-','-','-','-','-','-','-','-'])


        l_OC_t = l_CE + l_PE
        l_OC_t[:] = [x if x != 0 else '-' for x in l_OC_t]

        l_OC.append(l_OC_t)
    
    return l_OC


#############################################################
## Function to display option chain data based on
## expiry date. 
#############################################################
def display_oc_data(oc_full_data_edt, ed):

    ce_data_edt = oc_full_data_edt[ed]['CE']
    pe_data_edt = oc_full_data_edt[ed]['PE']

    ## prepare final data
    l_final_oc_data_edt = preprate_final_data(ce_data_edt, pe_data_edt)

    OC_col = ['c_OI', 'c_CHNG_IN_OI', 'c_VOLUME', 'c_IV', 'c_LTP', 'c_CHNG', 'c_BID_QTY', 'c_BID', 'c_ASK', 'c_ASK_QTY',  'STRIKE', 'p_BID_QTY', 'p_BID', 'p_ASK', 'p_ASK_QTY',  'p_CHNG', 'p_LTP', 'p_IV', 'p_VOLUME', 'p_CHNG_IN_OI', 'p_OI']
   
    pd.set_option('display.max_rows', None)

    df = pd.DataFrame(l_final_oc_data_edt)
    df.columns = OC_col

    print('')
    #print(df)
    print(tabulate(df, headers='keys', tablefmt='fancy_grid'))


#############################################################
## Main function
#############################################################
if __name__ == '__main__':


    #x = PrettyTable()

    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'               
    headers={'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}

    oc_data = {}
    refresh_time = 30 # in seconds

    pd.set_option('display.max_rows', None)
    #pd.set_option('display.max_columns', None)

    success, oc_json_object = create_OC_JSON_object(url, headers, 10) ## Populate all expiry dates
    
    if success:
        
        oc_full_data = create_edate_data_dict(oc_json_object)
        delete_unwanted_fields(oc_full_data)
        expiry_dates = list(oc_full_data.keys())

        ed_i = 0 ## Set expiry date index to 0 to fetch first expiry date
        
        #print(expiry_dates[ed_i]) ## Print first expiry date
        print(expiry_dates[ed_i])
        print('=====================')

        # Show Option chain final data
        display_oc_data(oc_full_data, expiry_dates[ed_i])

        l_sec = time.localtime().tm_sec

        while True:

            if kbhit():
                key = ord(getch())
                key_pressed = str(find_2dl_index(keys_mapping,key))
                if key_pressed == 'ESC': #ESC
                    break
                else:    
                    if key_pressed != None:
                        if key_pressed == 'UP':
                            if ed_i == 0:
                                ed_i = len(expiry_dates) - 1
                            else:
                                ed_i = ed_i - 1

                        if key_pressed == 'DOWN':
                            if ed_i == len(expiry_dates) - 1 :
                                ed_i = 0
                            else:
                                ed_i = ed_i + 1
    
                        os.system('clear')
                        print(expiry_dates[ed_i])
                        print('=====================')

                        display_oc_data(oc_full_data, expiry_dates[ed_i])  

    else:
        print('Error: Failed to scrap data..')
            