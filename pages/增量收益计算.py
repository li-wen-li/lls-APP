
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import os
from datetime import datetime as dt
import scipy.stats as stats
from pylab import mpl
from bokeh.plotting import figure
import plotly.express as px

## 一些函数
# 颜色设置
def set_color(num, color1, color2):
    if num <= -0.1:
     return f"color: {color1}; border: 1px solid currentcolor;"  
    elif num < 0:
     return f"color: {color2};"  
    elif num < 1:
     return f"background: {color1}"
    elif num > 1:
     return f"background: {color2}"
    else:
     None

# str to date
def to_date(date):
    return dt.strptime(date, '%Y-%m-%d')

st.markdown("""
# 增量订单计算
:corn: 功能：帮助市场部门根据预估增量计算对应的订单数

:peach: 使用方法：
1. 从SQLambda DA-3369.0获取最近两周数据并下载Excel文件，点击 **Browse files**上传该文件。
2. 点击展开 **数据概览** 查看最近数据
3. 点击展开 **增量计算** 选择最近新增占比/曝光比例/转化率等节点数据，或进行自定义设置。
4. 输入预估增量用户数
""")
st.markdown("---")
st.subheader("上传数据")
# 从lambda获取最近数据并在此上传
recent_data = st.file_uploader(label = ":open_file_folder: 上传近两周数据",
                                type=".xlsx")
st.markdown("---")

if recent_data:
    
    df = pd.read_excel(recent_data)
    
    all_user = df.loc[(df['生命周期']=='ALL') & (df["职业"]=='ALL'), ~df.columns.isin(['达尔文-49 加群率','达尔文-1 加群率','BELL-12 加群率'])].set_index('data_date')
    t0_user_all = df.loc[(df['生命周期']=='T=0') & (df['职业']=='ALL'),~df.columns.isin(['达尔文-49 加群率','达尔文-1 加群率','BELL-12 加群率','DARWIN-49 售前页曝光率','DARWIN-1 售前页曝光率','BELL-12 售前页曝光率'])].set_index('data_date')
    t0_user = df.loc[(df['生命周期']=='T=0') & (df['职业']!='ALL'),:]
    profsn_t0 = t0_user.groupby(['data_date', '职业'])['用户数'].sum().unstack().reset_index()

    profsn_num = profsn_t0.set_index('data_date')
    profsn_pct = profsn_num.div(profsn_num.sum(axis = 1), axis = 0)
    profsn_pct.columns = ['上班族占比', '其他占比', '其他在校生占比', '大学生占比', '自由派占比', '高中生占比']

    profsn_merged = pd.merge(profsn_num,profsn_pct, how = 'inner', on = 'data_date').iloc[:, [0,3,4,5,2,1,6,9,10,11,8,7]]
    
    st.subheader("近日数据概览")
    st.markdown(":point_down:点击下拉选择你想要查看的数据")
    choice_of_data = ['点击展开近日数据概览','总体数据概览', 'T=0用户数以及售前页转化率', '各职业新增用户趋势', '新增用户职业占比']

    option = st.selectbox(
        '查看数据类型',
        options = choice_of_data,
        index = 0,
        label_visibility = "collapsed"
        )
    if option == '点击展开近日数据概览':
        st.markdown("")
        
    if option == '总体数据概览':
        st.dataframe(all_user.sort_values("data_date").style.set_properties(**{'background-color': '#e6f2ff'}, subset = ['用户数','DARWIN-49 售前页转化率', 'DARWIN-1 售前页转化率', 'BELL-12 售前页转化率']).format("{:.1%}", 
                                                subset = ['DARWIN-49 售前页曝光率', 'DARWIN-49 售前页转化率', 'DARWIN-1 售前页曝光率', 'DARWIN-1 售前页转化率', 'BELL-12 售前页曝光率',
                                                         'BELL-12 售前页转化率']))

    if option == '新增用户职业占比':
        st.dataframe(profsn_merged.style.applymap(set_color, color1 = '#ADD8E6', color2 = '#E0FFFF').format("{:.1%}", 
                    subset = ['上班族占比','其他占比', '其他在校生占比','大学生占比','自由派占比','高中生占比']).set_caption('各职业每日总新增人数以及占比'),
                    use_container_width=True)

    if option == 'T=0用户数以及售前页转化率':
        st.dataframe(t0_user_all.style.format("{:.1%}",
                    subset = ['DARWIN-49 售前页转化率', 'DARWIN-1 售前页转化率','BELL-12 售前页转化率']),
                    use_container_width=True)
            
    if option == '各职业新增用户趋势':    
        pro_graph = px.line(profsn_t0, 
                            x = 'data_date', 
                            y=['大学生', '上班族','自由派','高中生', '其他在校生'])
        st.plotly_chart(pro_graph, use_container_width=True)
    st.markdown("---")

    st.subheader("增量计算")

    with st.expander(":chart_with_upwards_trend: 增量计算"): #, expanded = True
        col1, col2, col3 = st.columns(spec = [1.5,1,1.5],
                                      gap = "small")

        with col1:
            st.header("转化率")

            t0_user_conv = t0_user.groupby(['职业'])['DARWIN-49 售前页转化率','DARWIN-1 售前页转化率','BELL-12 售前页转化率'].mean()
            t0_user_conv.columns = ['DARWIN-49', 'DARWIN-1', 'BELL-12']

            haha = st.radio(label = "选择转化率参数",
                            options = ('近日均值','自定义'))

            if haha == '近日均值':
                t0_user_conv = t0_user_conv
                st.dataframe(t0_user_conv.style.format("{:.1%}"),use_container_width=True)

            if haha == '自定义':
                prof_rate_to_change = st.multiselect(
                    label = '选择你想要修改的职业(可以多选):',
                    options = ['大学生', '上班族','自由派','高中生','其他在校生'],
                    key = '转化率'
                    #default = ['大学生', '上班族']
                )
                conv_rate_to_change = st.multiselect(
                    label = '选择你想要修改转化率的SKU(可以多选):',
                    options = ["DARWIN-49",'DARWIN-1','BELL-12']
                )
                if conv_rate_to_change:
                    orig_user_conv = t0_user_conv
                    for prof in prof_rate_to_change:
                        for rate in conv_rate_to_change:
                            prof_rate = st.number_input(label = '修改 ' + prof + rate + ' 转化率至：',
                                                        value = orig_user_conv.at[prof, rate])
                            orig_user_conv.loc[prof,rate] = prof_rate
                    t0_user_conv = orig_user_conv
                    st.dataframe(orig_user_conv.style.format("{:.1%}"),use_container_width=True)

        with col2:
            st.header("新增占比")

            mean_prof_pct = profsn_pct.mean().to_frame()
            mean_prof_pct.columns = ['占比']

            hehe = st.radio(label = "选择各职业占比",
                            options = ('近日均值','自定义'))
            if hehe == '近日均值':
                mean_prof_pct = mean_prof_pct
                st.dataframe(mean_prof_pct.style.format("{:.0%}"),use_container_width=True)

            if hehe == '自定义':
                prof_pct_to_change = st.multiselect(
                    label = '选择你想要修改的职业(需要选择两个或更多):',
                    options = ['大学生', '上班族','自由派','高中生','其他在校生'],
                    key = '职业占比'
                    #default = ['大学生', '上班族']
                )
                if prof_pct_to_change:
                    orig_user_pct = mean_prof_pct
                    for prof in prof_pct_to_change:
                        prof = prof + '占比'
                        prof_pct = st.number_input(label = '修改 ' + prof + ' 的占比至:',
                                                value = orig_user_pct.at[prof,'占比'] ,
                                                min_value = 0.0, 
                                                max_value = 1.0,
                                                step = 0.01)
                        
                        orig_user_pct.loc[prof,:] = prof_pct
                    mean_prof_pct = orig_user_pct
                    st.dataframe(mean_prof_pct.style.format("{:.0%}"),use_container_width=True)
                    st.write(mean_prof_pct.sum().round(2))

        with col3:
            st.header("曝光占比")

            mean_exp_pct = t0_user.groupby(['职业'])['DARWIN-49 售前页曝光率', 'DARWIN-1 售前页曝光率', 'BELL-12 售前页曝光率'].mean()
            mean_exp_pct.columns = ['DARWIN-49', 'DARWIN-1', 'BELL-12']

            xixi = st.radio(label = "选择各职业曝光占比策略",
                            options = ('近日均值','自定义'))
            if xixi == '近日均值':
                mean_exp_pct = mean_exp_pct
                st.dataframe(mean_exp_pct.style.format("{:.0%}"),use_container_width=True)
            if xixi == '自定义':
                prof_exp_to_change = st.multiselect(
                    label = '选择你想要修改的职业(可以多选)',
                    options = ['大学生', '上班族','自由派','高中生','其他在校生'],
                    key = '职业曝光占比1'
                )
                exp_to_change = st.multiselect(
                    label = '选择你想要修改的SKU曝光率',
                    options = ['DARWIN-49', 'DARWIN-1', 'BELL-12'],
                    key = '职业曝光占比2'
                )

                if(exp_to_change):
                    orig_user_exp = mean_exp_pct
                    for prof in prof_exp_to_change:
                        for sku in exp_to_change:
                            prof_exp = st.number_input(
                                label = '修改 ' + prof + sku + '的曝光率至：',
                                value = orig_user_exp.at[prof, sku])
                            orig_user_exp.loc[prof,sku] = prof_exp
                    mean_exp_pct = orig_user_exp
                    st.dataframe(mean_exp_pct.style.format("{:.0%}"),use_container_width=True)
    st.markdown("---")

    st.subheader("计算结果")

    with st.expander(":blue_book:"):
    # 输入预计新增用户数
        col1, col2, col3= st.columns(spec = [1,1,2])
        with col1: 
            st.write(":one: **输入预估用户数以及当前订单收益**")
            proj_user_num = st.number_input(label = '**预计新增用户数**',
                                                value = 3000,
                                                step = 100)
            recent_resale = st.file_uploader(label = '**上传群产数据**', type = ".xlsx")
            
            ##st.number_input(label = 'Bell群产')
            
        with col2:
            st.write(":two: **预估订单数**")
            prof_pct = pd.concat([mean_prof_pct]*3, axis=1)
            prof_pct.columns = ['DARWIN-49', 'DARWIN-1', 'BELL-12'] 

            proj_prof_num = proj_user_num * prof_pct
            proj_prof_num = proj_prof_num.T.round(0)
            proj_prof_num.columns = ['上班族','其他', '其他在校生','大学生','自由派','高中生']

            # 各职位对应各SKU的售前曝光人数
            proj_prof_exp_num = proj_prof_num.mul(mean_exp_pct.T)
        
            ## 各职业对应SKU订单数
            proj_prof_order_num = proj_prof_exp_num.mul(t0_user_conv.T)
            st.write("**各职业订单数**")
            st.dataframe(proj_prof_order_num.style.format(precision = 1),
                        use_container_width = True)
            proj_all_order = proj_prof_order_num.T.sum().to_frame()
            proj_all_order.columns = ['订单数']
            st.write("**汇总订单数**")
            st.dataframe(proj_all_order.style.format(precision = 1),use_container_width=True)
        with col3:
            st.write(":three: **预估收益**")
            if recent_resale:
                recent_resale = pd.read_excel(recent_resale)
                st.write("**当前入群人均收益**")
                
                mean_prof_value = recent_resale.loc[:,['group_type', 'sub_profession','人均收益']].reset_index().pivot('group_type', 'sub_profession', '人均收益')
                st.dataframe(mean_prof_value.style.format(precision = 0),use_container_width=True )


                st.write("**预估各职业人群新增收益**")
                order_num = proj_prof_order_num.loc[['DARWIN-49','DARWIN-1']]
                group_num = order_num*0.9
                proj_income = group_num.mul(mean_prof_value)
                st.dataframe(proj_income.style.format(precision = 0),use_container_width=True)

                st.metric(label = '总进群收益', 
                          value = proj_income.to_numpy().sum().round())
                st.metric(label = '增量人均价值',
                          value = (proj_income.to_numpy().sum()/proj_user_num).round(2))
