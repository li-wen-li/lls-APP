import streamlit as st
import pandas as pd

upload_data = st.file_uploader(label = '上传表格',
                                accept_multiple_files=False)

if upload_data is not None:
    data_csv = pd.read_excel(upload_data)
    st.write(data_csv)
