import streamlit as st
import investpy
import pandas as pd
from datetime import datetime, timedelta
import os
import tempfile
import base64


def fetch_economic_calendar(countries, importances, from_date, to_date):
    if from_date == to_date:
        # Set to_date to one day ahead if it's the same as from_date
        to_date += timedelta(days=1)
    data = investpy.economic_calendar(countries=countries, importances=importances, from_date=from_date.strftime('%d/%m/%Y'), to_date=to_date.strftime('%d/%m/%Y'))
    return data

def main():
    st.title('Economic Calendar')
    
    st.sidebar.title('Settings')
    countries = st.sidebar.multiselect('Select countries', ['euro zone','united kingdom' ,'united states', 'morocco'])
    importances = st.sidebar.multiselect('Select importance', ['Low', 'Medium', 'High'])
    from_date = st.sidebar.date_input("From Date", value=datetime.today())
    to_date = st.sidebar.date_input("To Date", value=datetime.today() + timedelta(days=1))  
    
    if to_date < from_date:
        st.error("Error: 'To Date' should be greater than or equal to 'From Date'. Please adjust the date range.")
        return
    
    importances_lower = [importance.lower() for importance in importances]
    
    data = fetch_economic_calendar(countries, importances_lower, from_date, to_date)
    
    if 'id' in data.columns:
        data.drop(columns=['id'], inplace=True)
    
    st.write(data)

    if st.button('Download as Excel'):
        df = pd.DataFrame(data)
        
        # Save DataFrame to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmpfile:
            df.to_excel(tmpfile.name, index=False)
        
        # Provide download link to the generated file
        with open(tmpfile.name, 'rb') as f:
            data = f.read()
            b64_data = base64.b64encode(data).decode('utf-8')
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_data}" download="economic_calendar_data.xlsx">Download Excel file</a>'
            st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
