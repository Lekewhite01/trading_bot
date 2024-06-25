import streamlit as st
import warnings
from bot import *
warnings.filterwarnings("ignore")


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
placeholder = st.empty()

with placeholder.form("login_form", clear_on_submit=True):
    acc_type = st.text_input('Account Type', value=config.acc_type)
    acc_id = st.text_input('Account ID', value=config.acc_id)
    username = st.text_input("Username", value=config.username)
    password = st.text_input('Password', type='password', value=config.password)
    api_key = st.text_input('API Key', type='password', value=config.api_key)
    submit = st.form_submit_button("Submit")

if submit:
    # Clear the form from the page
    placeholder.empty()
    # Initialize IG service
    try:
        # ig_service = IGService(config.username, config.password, config.api_key, config.acc_type,
        #                        config.acc_id)
        # ig_service.create_session(version='3')
        ig_service = igapi.IG(config.api_key, config.username, config.password, config.acc_id, config.acc_type)
        ig_service.login()
        st.success("You are now logged in to your session")
    except Exception as e:
        st.error(e)

    account = ig_service.account()
    st.write(account.loc['XQWAV', 'balance']['balance'])
    market = st.sidebar.selectbox("Choose an instrument",
    ("Forex", "Gold", "CFD", "Crypto", "Shares"),
    index=None,
    placeholder="Select Instrument")

creds = IGtokens(config.api_key, config.username, config.password, config.acc_type).login()
markets = search_markets(search_term="gold",
                            cst=creds["CST"],
                            token=creds["X_SECURITY_TOKEN"])
st.write(markets)