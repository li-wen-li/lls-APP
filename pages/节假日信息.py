import json
import pandas as pd
import urllib
from datetime import datetime
import streamlit as st



year = st.number_input(label = '输入查询年份',
                        min_value = 2015,
                        max_value = 2023,
                        step = 1)
st.write('当前查询年份为： ', year)
st.markdown('_以下节假日仅包含国家法定假日，不包含国外假日_')
st.write('法定节假日具体明细：')


lower_date = str(year) + '-01-01'
upper_date = str(year) + '-12-31'

## 假期调取API https://codeantenna.com/a/YdyMkicDne
dates = pd.date_range(lower_date, upper_date, freq="d").astype(str).tolist()
date_list=[s[5:] for s in dates]

holiday_url = "http://timor.tech/api/holiday/year/" + str(year)
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'}
req = urllib.request.Request(url=holiday_url, headers=headers)
x = urllib.request.urlopen(req).read().decode('utf-8')
x_json=json.loads(x)

y=pd.DataFrame()

for date in date_list:    
    try:       
        dfi=pd.DataFrame(
            list(x_json['holiday'][date].values()),
            index=list(x_json['holiday'][date].keys())
        )        
        dfii=dfi.T        
        y=pd.concat([y,dfii])    
    except:        
            continue

target_holidays = y[y['wage']>1]
target_holidays = target_holidays[['date', 'name']]

target_holidays.columns = ['日期','假日名称'] 
target_holidays

