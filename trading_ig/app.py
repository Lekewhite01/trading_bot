import streamlit as st
import warnings
import time
import os
# from bot import *
import technical_indicators
from trading_ig_config import config
from technical_indicators import *
from trading_performance import *
from trading_strategy import *
from ig_execute import *
warnings.filterwarnings("ignore")

session = st.session_state

# Set an environment variable to suppress warnings
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Ignore warnings
warnings.filterwarnings('ignore')

# Configure Streamlit app settings
st.set_page_config(layout="centered",
                   page_title="IG TRADING BOT",
                   page_icon="https://repository-images.githubusercontent.com/156847937/2ac66980-0f3d-11eb-8e62-693087aa1f67"
                   )

# ---To remove white spacing above app header---
# (Souce: https://stackoverflow.com/questions/71209203/remove-header-whitespacing-from-streamlit-hydralit)
st.write('<style>div.block-container{padding-top:0rem;}</style>', unsafe_allow_html=True)

# Hide the default "Made with Streamlit" footer
hide_default_format = """
      <style>
      footer {visibility: hidden;}
      </style>
      """
st.markdown(hide_default_format, unsafe_allow_html=True)

# Custom CSS to add an image to the title
custom_css = """
<style>
.title-container {
    display: flex;
    align-items: center;
}

.title-text {
    margin-left: 20px;
}
</style>
"""

# Use the custom CSS to style the title
st.markdown(custom_css, unsafe_allow_html=True)

# Create a title container with an image and text
st.markdown('<div class="title-container"><img src="https://th.bing.com/th/id/R.632537e5a1b2bec9433128a0595b2b96?rik=WnzqOdxi7%2boU8g&pid=ImgRaw&r=0" alt="Image" width="80"/><h1 class="title-text">IG Trading Bot</h1></div>', unsafe_allow_html=True)

# Create a placeholder for the form
with st.sidebar:
    placeholder = st.empty()
    
    with placeholder.form(key="login_form", clear_on_submit=False):
        acc_type = st.text_input('Account Type', key="acc_type", value=config.acc_type)
        acc_id = st.text_input('Account ID', key="acc_id", value=config.acc_number)
        username = st.text_input("Username", key="username", value=config.username)
        password = st.text_input('Password', key="password", type='password', value=config.password)
        api_key = st.text_input('API Key', key="api_key", type='password', value=config.api_key)
        submit = st.form_submit_button("Submit")

if submit:
    # Clear the form from the page
    # placeholder.empty()
    st.success("IG credentials loaded successfully")

# Initialize IG service
ig_service = IGService(session.username, session.password, session.api_key, session.acc_type,
                    session.acc_id)
ig_service.create_session(version='3')
ig_service = IG_connect()


def display_top_level_nodes():
    # ig_service = IG_connect()
    response = ig_service.fetch_top_level_navigation_nodes()
    df = response["nodes"]
    df = df[(df["name"]=='Forex') | (df["name"]=='Indices') | \
            (df["name"]=='Commodities Metals Energies') | (df["name"]=='Commodities Metals Energies (mini)') | \
            (df["name"]=='Shares - US (All Sessions)')]
    return df

market_df = display_top_level_nodes()
market_list = market_df["name"].tolist()
market = st.selectbox("Choose a market",
                market_list,
                index=None,
                placeholder="Select preferred market")

session.market = market
session.market_df = market_df

# st.write(session)
# if session.ig_service and session.market and session.market_df:
if session.market:
    node_id = session.market_df.loc[session.market_df["name"] == session.market, "id"].iloc[0]
    session.node_id = node_id

epic_list = ["epic_1", "epic_2", "epic_3"]
epic = st.selectbox("Choose Your epic",
                epic_list,
                index=None,
                placeholder="Select epic for your instrument")

col1, col2, col3, col4 = st.columns(4)

with col1:
    position_size = st.select_slider(
    "Select the number of units for trade",
    options=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
    session.position_size = position_size
    
with col2: 
    resolution = st.radio(
    "Select interval for RSI check",
    ["5Min", "10Min", "15Min", "20Min", "25Min", "30Min"])
    session.resolution = resolution
    
with col3:
    stop_increment = st.select_slider(
    "Select the trailing stop increment",
    options=["5", "10", "15", "20"])
    session.stop_increment = stop_increment
    
with col4:
    data_points = st.radio(
    "Select number of data points",
    ["250", "500", "1000"])
    session.data_points = data_points

with col1:
    runtime = st.select_slider(
    "Select trading strategy runtime",
    options=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
    session.runtime = runtime
    
with col2: 
    trading_frequency = st.radio(
    "Select interval for trading",
    ["5", "10", "15", "20", "25", "30"])
    session.trading_frequency = trading_frequency
    
with col3:
    min_stop_distance = st.number_input("Insert a number", value=0.01, placeholder="Type a number...")
    session.min_stop_distance = min_stop_distance
    
with col4:
    stop_distance = st.select_slider(
    "Select the trailing stop distance",
    options=["5", "10", "15", "20"])
    session.stop_distance = stop_distance

with col1:
    limit = st.radio(
    "Select limit",
    ["5", "10", "15"])
    session.limit = limit

execute = st.button("Execute Trade", use_container_width=True)
if execute:
    # Define trading parameters
    epic = "IX.D.FTSE.IFM.IP"  # Epic pairs to be included in the strategy
    pos_size = session.position_size  # max capital allocated/position size for any epic pair
    resolution = session.resolution  # resolution of ohlc data
    trailing_stop_increment = session.stop_increment
    num_points = session.data_points # number of data points
    runtime = session.runtime # run time of trading strategy in hours
    trading_frequency = session.trading_frequency  # frequency to trade in minutes - match to data resolution
    minimum_stop_distance = session.min_stop_distance  # minimum stop distance in % of the instruments traded
    trailing_stop_distance = session.stop_distance
    limit = session.limit

    trading = Trading(ig_service)
    
    # Retrieve currently open positions
    open_pos = trading.open_positions()
    st.write(open_pos)
    # Determine if open position is long or short
    long_short = ""
    if len(open_pos) > 0:
        open_pos_cur = open_pos[open_pos["epic"] == epic]
    
        if len(open_pos_cur) > 0:
            if open_pos_cur["direction"].tolist()[0] == "BUY":
                long_short = "long"
            elif open_pos_cur["direction"].tolist()[0] == "SELL":
                long_short = "short"
    
    
    # Return historic OHLC price data for the epic based on resolution and number of points.
    ohlc = trading.price_data(epic, resolution, num_points)
    
    """Set this for any instrument that has the trailing stop as a percentage and not in pips"""
    # trailing_stop_distance = str(ohlc.iloc[-1]['High']*minimum_stop_distance)
    
    # Calculate the signal for the trade based off the chosen strategy
    # signal = trading_strategy.MACD_Renko(technical_indicators.renko_merge(ohlc), long_short)
    signal = RSI(technical_indicators.RSI(ohlc,30), long_short)
    
    if len(signal) > 1:
        print(signal, "for", epic)
    else:
        print("No signal for", epic)
    
    if signal in ("BUY", "SELL"):
        trading.open_trade(
            signal, epic, pos_size, limit, trailing_stop_distance, trailing_stop_increment
        )
    
    elif signal == "Close":
        trading.close_trade(long_short, epic, open_pos_cur)
    
    elif signal == "Close_Buy":
        direction = "BUY"
        trading.close_trade(long_short, epic, open_pos_cur)
        trading.open_trade(
            direction,
            epic,
            pos_size,
            limit,
            trailing_stop_distance,
            trailing_stop_increment,
        )
    
    elif signal == "Close_Sell":
        direction = "SELL"
        trading.close_trade(long_short, epic, open_pos_cur)
        trading.open_trade(
            direction,
            epic,
            pos_size,
            limit,
            trailing_stop_distance,
            trailing_stop_increment,
        )
    
    starttime = time.time()
    timeout = time.time() + 60 * 60 * int(runtime)
    trading_summary = pd.DataFrame(
        columns=[
            "Date",
            "Duration (min)",
            "Net Profit",
            "Max Win",
            "Max Loss",
            "Winners",
            "Losers",
            "R Factor",
        ]
    )
    
    st.write(
        "\nPassthrough at ",
        time.strftime("%H:%M:%S %d-%m-%Y", time.localtime(time.time())),
        "\n",
    )
    
    session_duration = time.time() - starttime
    
    # Retrieve historical trade data for the length of the session
    trade_data = trading.transaction_history(int(session_duration * 1000))
    
    # Calculate trade performance for each trading interval
    trading_summary = measure_performance(
        trade_data, session_duration, trading_summary
    )
    if len(trading_summary) > 0:
        st.write("\n", trading_summary)
    else:
        st.write("\nNo closed trades in current session")
    
    # Sleep until ready for next trade
    time.sleep(int(trading_frequency) * 60)
# st.write(session)



