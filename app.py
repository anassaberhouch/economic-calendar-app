import streamlit as st
import investpy
import pandas as pd
from datetime import datetime, timedelta
import os
import tempfile
import base64
from PIL import Image
import math
from scipy.stats import norm

def fetch_economic_calendar(time_zone, countries, importances, from_date, to_date):
    if from_date == to_date:
        to_date += timedelta(days=1)
    data = investpy.economic_calendar(time_zone, countries=countries, importances=importances, from_date=from_date.strftime('%d/%m/%Y'), to_date=to_date.strftime('%d/%m/%Y'))
    return data

# Barrier Option Pricer
def barrier_option_pricer(option_type, barrier_level, strike_price, volatility, time_to_maturity, risk_free_rate=0.01):
    # Calculate d1 and d2
    d1 = (math.log(barrier_level / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_maturity) / (volatility * math.sqrt(time_to_maturity))
    d2 = d1 - volatility * math.sqrt(time_to_maturity)
    
    # Calculate option price based on option type
    if option_type == 'Up-and-Out':
        price = barrier_level * norm.cdf(d1) - strike_price * math.exp(-risk_free_rate * time_to_maturity) * norm.cdf(d2)
    elif option_type == 'Down-and-Out':
        price = -barrier_level * norm.cdf(-d1) + strike_price * math.exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2)
    elif option_type == 'Up-and-In':
        price = strike_price * math.exp(-risk_free_rate * time_to_maturity) * norm.cdf(d2) - barrier_level * norm.cdf(d1)
    elif option_type == 'Down-and-In':
        price = -strike_price * math.exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d2) + barrier_level * norm.cdf(-d1)
    else:
        return "Invalid option type"
    return price

# Binary Option Pricer
def binary_option_pricer(option_type, strike_price, underlying_price, volatility, time_to_maturity, risk_free_rate=0.01):
    # Calculate d1
    d1 = (math.log(underlying_price / strike_price) + (risk_free_rate + 0.5 * volatility ** 2) * time_to_maturity) / (volatility * math.sqrt(time_to_maturity))
    
    # Calculate option price based on option type
    if option_type == 'Call':
        price = math.exp(-risk_free_rate * time_to_maturity) * norm.cdf(d1)
    elif option_type == 'Put':
        price = math.exp(-risk_free_rate * time_to_maturity) * norm.cdf(-d1)
    else:
        return "Invalid option type"
    return price

def main():
    logo_path = "CIB_LOGO-removebg-preview.png"
    logo_image = Image.open(logo_path)
    st.image(logo_image, width=100)
    
    st.title('AWB Finance Toolkit')
    
    # Navigation buttons
    st.write("### Select a page:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Economic Calendar"):
            st.session_state.page = "Economic Calendar"
    with col2:
        if st.button("Pricer"):
            st.session_state.page = "Pricer"
    
    # Default page
    if "page" not in st.session_state:
        st.session_state.page = "Economic Calendar"
    
    if st.session_state.page == "Economic Calendar":
        st.title("Economic Calendar")
        
        st.sidebar.title('Settings')
        countries = st.sidebar.multiselect('Select countries', ['euro zone' ,'united states', 'morocco','united kingdom'])
        importances = st.sidebar.multiselect('Select importance', ['Low', 'Medium', 'High'])
        from_date = st.sidebar.date_input("From Date", value=datetime.today())
        to_date = st.sidebar.date_input("To Date", value=datetime.today() + timedelta(days=1))  
        
        if to_date < from_date:
            st.error("Error: 'To Date' should be greater than or equal to 'From Date'. Please adjust the date range.")
            return
        time_zone='GMT +1:00'
        importances_lower = [importance.lower() for importance in importances]
        
        data = fetch_economic_calendar(time_zone, countries, importances_lower, from_date, to_date)
        
        if 'id' in data.columns:
            data.drop(columns=['id'], inplace=True)
        
        st.write(data)

        if st.button('Download as Excel'):
            df = pd.DataFrame(data)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmpfile:
                df.to_excel(tmpfile.name, index=False)
            
            with open(tmpfile.name, 'rb') as f:
                data = f.read()
                b64_data = base64.b64encode(data).decode('utf-8')
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_data}" download="economic_calendar_data.xlsx">Download Excel file</a>'
                st.markdown(href, unsafe_allow_html=True)

    elif st.session_state.page == "Pricer":
        st.title("Pricer")
        
        st.write("### Select an option type:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Barrier Options"):
                st.session_state.option_type = "Barrier Options"
        with col2:
            if st.button("Binary Options"):
                st.session_state.option_type = "Binary Options"
        
        if "option_type" in st.session_state:
            if st.session_state.option_type == "Barrier Options":
                st.title("Barrier Options Pricer")
                
                barrier_option_type = st.selectbox('Barrier Option Type', ['Up-and-Out', 'Down-and-Out', 'Up-and-In', 'Down-and-In'])
                barrier_level = st.number_input('Barrier Level', value=100.0)
                barrier_strike_price = st.number_input('Strike Price', value=100.0)
                barrier_volatility = st.number_input('Volatility', value=0.2)
                barrier_time_to_maturity = st.number_input('Time to Maturity', value=1.0)

                if st.button('Calculate Barrier Option Price'):
                    barrier_option_price = barrier_option_pricer(barrier_option_type, barrier_level, barrier_strike_price, barrier_volatility, barrier_time_to_maturity)
                    st.write(f'Barrier Option Price: {barrier_option_price}')
            
            elif st.session_state.option_type == "Binary Options":
                st.title("Binary Options Pricer")
                
                binary_option_type = st.selectbox('Binary Option Type', ['Call', 'Put'])
                binary_strike_price = st.number_input('Strike Price', value=100.0)
                binary_underlying_price = st.number_input('Underlying Price', value=100.0)
                binary_volatility = st.number_input('Volatility', value=0.2)
                binary_time_to_maturity = st.number_input('Time to Maturity', value=1.0)

                if st.button('Calculate Binary Option Price'):
                    binary_option_price = binary_option_pricer(binary_option_type, binary_strike_price, binary_underlying_price, binary_volatility, binary_time_to_maturity)
                    st.write(f'Binary Option Price: {binary_option_price}')

if __name__ == "__main__":  
    main()