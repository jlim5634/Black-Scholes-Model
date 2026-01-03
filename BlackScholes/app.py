#handles user unput and displays output
#calls other modules

import streamlit as st
from data import get_stock_price
from plots import Plots
from BlackScholes import BlackScholes
import numpy as np


#UI Layout
st.set_page_config(
    page_title="Black-Scholes Option Pricing Model",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.title("📊 Black-Scholes Model")
    linkedin_url = "https://www.linkedin.com/in/joshualim2006"
    st.markdown(f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;">`Joshua Lim`</a>', unsafe_allow_html=True)

    ticker = st.text_input("StockTicker", "AAPL")

    S = get_stock_price(ticker) if ticker else 100.0
    st.write(f"Current Stock Price: ${S:.2f}")

    K = st.number_input("Strike Price", min_value=0.0, value=100.0)
    T = st.number_input("Time to Maturity (years)", min_value=0.1, value=1.0)
    sigma = st.number_input("Volatility (σ)", min_value=0.0, value=0.2)
    r = st.number_input("Risk-Free Rate", min_value=0.0, value=0.05)

    # st.markdown("---")
    # run_model = st.button("Calculate")

st.markdown("""
<style>
.metric-box {
    padding: 1.2rem;
    border-radius: 12px;
    text-align: center;
    font-weight: bold;
}
.call-box {
    background-color: #27a567;
}
.put-box{
    background-color: #de0a26;
}
/* Adjust the size and alignment of the CALL and PUT value containers */
.metric-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 8px; /* Adjust the padding to control height */
    width: auto; /* Auto width for responsiveness, or set a fixed width if necessary */
    margin: 0 auto; /* Center the container */
}

/* Custom classes for CALL and PUT values */
.metric-call {
    background-color: #90ee90; /* Light green background */
    color: black; /* Black font color */
    margin-right: 10px; /* Spacing between CALL and PUT */
    border-radius: 10px; /* Rounded corners */
}

.metric-put {
    background-color: #ffcccb; /* Light red background */
    color: black; /* Black font color */
    border-radius: 10px; /* Rounded corners */
}

/* Style for the value text */
.metric-value {
    font-size: 1.5rem; /* Adjust font size */
    font-weight: bold;
    margin: 0; /* Remove default margins */
}

/* Style for the label text */
.metric-label {
    font-size: 1rem; /* Adjust font size */
    opcacity: 0.8;
    margin-bottom: 4px; /* Spacing between label and value */
}

</style>
""", unsafe_allow_html=True)



# #Button logic
# if run_model:
BS = BlackScholes(time_to_maturity=T, strike=K, current_price=S, volatility = sigma, interest_rate=r)
call_price, put_price = BS.price() #call to populate call_price and greeks

greeks = BS.greeks()

metric_container = st.container()
col1, col2 = metric_container.columns(2)

with col1:
    st.markdown(f"""
    <div class="metric-box call-box">
        <div class="metric-label">CALL PRICE</div>
        <div class="metric-value">${call_price:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-box put-box">
        <div class="metric-label">PUT PRICE</div>
        <div class="metric-value">${put_price:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1,1], gap="small")


st.subheader("Greeks")

g1, g2, g3, g4, g5 = st.columns(5)


g1.metric("Call Δ", f"{greeks['call_delta']:.4f}")
g2.metric("Put Δ", f"{greeks['put_delta']:.4f}")
g3.metric("Gamma", f"{greeks['gamma']:.4f}")
g4.metric("Theta", f"{greeks['call_theta']:.4f}")
g5.metric("Vega", f"{greeks['vega']:.4f}")

st.subheader("Rho")
r1, r2 = st.columns(2)
r1.metric("Call ρ", f"{greeks['call_rho']:.4f}")
r2.metric("Put ρ", f"{greeks['put_rho']:.4f}")

plots = Plots()

st.markdown("---")
st.subheader("2D Option Price HeatMaps")

spot_range = np.linspace(S*0.8, S*1.2, 10)
vol_range = np.linspace(0.1,0.5, 10)
call_grid, put_grid = plots.generate_price_grid(BS, spot_range, vol_range)

h1, h2 = st.columns(2)

#2d heatmap
with h1:
    st.caption("Call Price Sensitivity")
    st.pyplot(plots.plot_call_heatmap(call_grid, spot_range, vol_range))
with h2:
    st.caption("Put Price Sensitivity")
    st.pyplot(plots.plot_put_heatmap(put_grid, spot_range, vol_range))

#3d heatmap
st.markdown("---")
st.subheader("3D Option Price Sensitivity")
s1, s2 = st.columns(2)

with s1:
    st.plotly_chart(
        plots.plot_call_surface(call_grid, spot_range, vol_range),
        use_container_width=True
    )
with s2:
    st.plotly_chart(
        plots.plot_put_surface(put_grid, spot_range, vol_range),
        use_container_width=True
    )
    
        



    


