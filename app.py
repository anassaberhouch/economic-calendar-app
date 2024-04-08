import streamlit as st
import investpy
import pandas as pd
from datetime import datetime, timedelta


def fetch_economic_calendar(countries, importances, from_date, to_date):
    data = investpy.economic_calendar(countries=countries, importances=importances, from_date=from_date, to_date=to_date)
    return data


def main():
    st.title('Economic Calendar')
    
    
    st.sidebar.title('Settings')
    countries = st.sidebar.multiselect('Select countries', ['euro zone', 'united states', 'morocco'])
    importances = st.sidebar.multiselect('Select importance', ['Low', 'Medium', 'High'])
    from_date = st.sidebar.date_input("From Date", value=datetime.today())
    to_date = st.sidebar.date_input("To Date", value=datetime.today() + timedelta(days=1))  
    
    
    if to_date < from_date:
        st.error("Error: 'To Date' should be greater than 'From Date'. Please adjust the date range.")
        return
    
    
    importances_lower = [importance.lower() for importance in importances]
    
    
    from_date_str = from_date.strftime('%d/%m/%Y')
    to_date_str = to_date.strftime('%d/%m/%Y')
    
    
    if countries:
        data = fetch_economic_calendar(countries, importances_lower, from_date_str, to_date_str)
        if 'id' in data.columns:
            data.drop(columns=['id'], inplace=True)  
        st.write(data)

        if st.button('Download as Excel'):
            df = pd.DataFrame(data)
            df.to_excel("economic_calendar_data.xlsx", index=False)
            st.success("Data downloaded successfully!")
    else:
        st.warning('Please select at least one country.')

if __name__ == "__main__":
    main()
