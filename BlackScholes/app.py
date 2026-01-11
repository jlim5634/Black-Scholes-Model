#handles user unput and displays output
#calls other modules

import streamlit as st
from data import get_stock_price
from plots import Plots
from BlackScholes import BlackScholes
import numpy as np
import datetime
import yfinance as yf
import pandas as pd
from database import create_table, save_calculation, get_calculations, initialize_db, get_connection, save_output, get_outputs
import sqlite3
from scenario import ShockScenario

create_table()
initialize_db()


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

   
    use_custom_price = st.sidebar.checkbox("Use custom current (spot) price?", value=False)

    if use_custom_price:
        S = st.number_input(
            "Enter Current (Spot) Price",
            min_value=0.0,
            value=100.0,
            step=0.01
        )
    else:
        ticker = st.text_input("StockTicker", "AAPL")
        ticker_obj = yf.Ticker(ticker)

        hist = ticker_obj.history(period="1y")
        st.subheader(f"Historical Prices for {ticker} (1 yr)")
        st.line_chart(hist['Close'])
        hist['Returns'] = hist['Close'].pct_change()
        hist_vol = hist['Returns'].std() * (252**0.5) #Annualized
        st.write(f"Historical Volatility (1 year): {hist_vol*100:.2f}%")

        S = get_stock_price(ticker) if ticker else 100.0
        st.write(f"Current Stock Price: ${S:.2f}")

    K = st.number_input("Strike (Purchase) Price", min_value=0.0, value= float(round(S / 5) * 5))
    st.caption(f"Default strike set to nearest ATM")

    expiry_date = st.date_input(
        "Expiration Date 📅",
        value=datetime.date.today() + datetime.timedelta(days=30),  # default = 30 days ahead
        min_value=datetime.date.today() + datetime.timedelta(days=1)  # cannot pick today or past
    )

    T = (expiry_date - datetime.date.today()).days / 365
    st.caption(f"Time to maturity (years): {T:.4f}")
    sigma = st.number_input("Volatility (σ)", min_value=0.0, value=0.2)
    r = st.number_input("Risk-Free Rate", min_value=0.0, value=0.05)

    market_price = st.sidebar.number_input(
        "Market Option Price (optional)",
        min_value = 0.0,
        value = 0.0,
        step=0.01
    )

    option_type = st.sidebar.radio(
        "Option Type for Implied Volatility (IV)",
        ["Call", "Put"]
    )

    st.sidebar.subheader("Scenario Shocks")

    spot_shock_pct = st.sidebar.slider(
        "Future Spot Shock (%)",
        -50, 50, 0
    ) / 100

    vol_shock_pct = st.sidebar.slider(
        "Volatility Spot Shock (%)",
        -50, 50, 0
    ) / 100

    BS = BlackScholes(time_to_maturity=T, strike=K, current_price=S, volatility = sigma, interest_rate=r)
    call_price, put_price = BS.price() #call to populate call_price and greeks

    scenario = ShockScenario(
        spot_shock = spot_shock_pct,
        vol_shock = vol_shock_pct
    )

    S_shocked, sigma_shocked = scenario.apply(S, sigma)

    BS_shocked = BlackScholes(time_to_maturity=T, strike=K, current_price=S_shocked, volatility = sigma_shocked, interest_rate=r)
    call_price_shocked, put_price_shocked = BS_shocked.price()

    call_pnl_value = call_price_shocked - call_price
    put_pnl_value = put_price_shocked - put_price

    if market_price > 0:
        st.sidebar.caption(f"Input volatility: {sigma*100:.2f}%")
        def implied_volatility(target_price, BS, option_type="call", tol=1e-6, max_iter=100):
            low, high = 0.001, 5.0 #range for volatility
            for i in range(max_iter):
                mid = (low + high) / 2
                BS.sigma = mid
                call_price, put_price = BS.price()
                price = call_price if option_type=="call" else put_price

                if abs(price- target_price) < tol:
                    return mid #bc found
                elif price > target_price:
                    high = mid
                else:
                    low = mid
            return mid
        iv = implied_volatility(market_price, BS, option_type.lower)
        st.sidebar.success(f"Market-Implied Volatility: {iv*100:.2f}%")


    moneyness = S / K

    if 0.95 <= moneyness <= 1.05:
        moneyness_label = "Value At-the-Money (ATM)"
        color = "orange"
    elif moneyness > 1.05:
        moneyness_label = "Value In-the-Money (ITM)"
        color = "green"
    else:
        moneyness_label = "Value Out-the-Money (OTM)"
        color = "red"

    st.markdown(
        f'<span style="font-weight:bold; color:{color};">Moneyness: {moneyness_label}</span>',
        unsafe_allow_html=True
    )       

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


greeks = BS.greeks()

st.markdown("---")
st.subheader("Save this calculation")

option_choice = st.selectbox("Option Type to Save", ["call", "put"])

if st.button("Save Calculation"):
    if option_choice == "call":
        option_price = call_price
        delta_val = greeks["call_delta"]
        rho_val = greeks["call_rho"]
    else:
        option_price = put_price
        delta_val = greeks["put_delta"]
        rho_val = greeks["put_rho"]

    #save greeks
    input_id = save_calculation(
        ticker=ticker if 'ticker' in locals() else None,
        spot_price=S,
        strike_price=K,
        time_to_maturity=T,
        volatility=sigma * 100,
        risk_free_rate=r * 100,
        option_type=option_choice,
        option_price=option_price,
        delta=delta_val,
        gamma=greeks["gamma"],
        theta=greeks["call_theta"] if option_choice=="call" else greeks["put_theta"],
        vega=greeks["vega"],
        rho=rho_val
    )

    save_output(
        input_id=input_id,
        call_grid=st.session_state["call_grid"],
        put_grid=st.session_state["put_grid"],
        vol_shock=None,
        call_pnl=st.session_state["call_pnl"],
        put_pnl=st.session_state["put_pnl"]
    )


    st.success(f"{option_choice.title()} calculation saved to database!")

st.markdown("---")
st.subheader("Calculation Input History")

history = get_calculations(limit=50)

if history:
    columns = [
        "ID", "Timestamp", "Ticker", "Spot Price", "Strike Price",
        "Time to Maturity (years)", "Volatility (%)", "Risk-Free Rate (%)", "Option Type",
        "Option Price", "Delta", "Gamma", "Theta", "Vega", "Rho"
    ]

    df_history = pd.DataFrame(history, columns=columns)

    st.dataframe(df_history)

else:
    st.info("No inputs saved yet")

st.subheader("Calculation Output History")

outputs = get_outputs(limit=50)

if outputs:
    df_outputs = pd.DataFrame(outputs, columns=[
        "Output ID",
        "Input ID",
        "Ticker",
        "Spot",
        "Strike",
        "Vol Shock",
        "Timestamp"
    ])

    st.dataframe(df_outputs)
else:
    st.info("No calulcation outputs saved yet")


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
g3.metric("Gamma", f"{greeks['gamma']:.6f}")
g4.metric("Theta", f"{greeks['call_theta']:.4f}")
g5.metric("Vega", f"{greeks['vega']:.6f}")

st.subheader("Rho")
r1, r2 = st.columns(2)
r1.metric("Call ρ", f"{greeks['call_rho']:.4f}")
r2.metric("Put ρ", f"{greeks['put_rho']:.4f}")

plots = Plots()

st.markdown("---")
st.subheader("2D Option Price HeatMaps")

spot_range = np.linspace(K*0.85, K*1.15, 10)
vol_range = np.linspace(0.1,0.5, 10)
call_grid, put_grid = plots.generate_price_grid(BS, spot_range, vol_range)
st.session_state["call_grid"] = call_grid
st.session_state["put_grid"] = put_grid

h1, h2 = st.columns(2)

#2d heatmap
with h1:
    st.caption("Call Price Sensitivity")
    st.pyplot(plots.plot_call_heatmap(call_grid, spot_range, vol_range))
with h2:
    st.caption("Put Price Sensitivity")
    st.pyplot(plots.plot_put_heatmap(put_grid, spot_range, vol_range))


#Greek sens chart comparison
st.subheader("Greek Sensivity Chart")
greek_options = {
    "call_delta", "put_delta", "gamma",
    "call_theta", "put_theta", "vega",
    "call_rho", "put_rho"
}
selected_greeks = st.multiselect("Select one or more Greeks to plot", greek_options, default=["call_delta"]) #multiselect for comparison
if selected_greeks:
    plt_multi = plots.greek_sens_multi(BS, S, selected_greeks)
    st.pyplot(plt_multi)
else:
    st.info("Please select as least one Greek to display the chart")


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

#PNL heatmap
st.markdown("---")
st.subheader("Call & Put Option PnL Heatmaps")
st.subheader("Call & Put Option PnL Heatmaps")

# Call PnL
call_pnl_png = plots.pnl_heatmap_single(BS, S, K, option_type="call")
st.image(call_pnl_png, width=700)

# Put PnL
put_pnl_png = plots.pnl_heatmap_single(BS, S, K, option_type="put")
st.image(put_pnl_png, width=700)

call_pnl = np.maximum(spot_range - K, 0) - call_price
put_pnl = np.maximum(K - spot_range, 0) - put_price
st.session_state["call_pnl"] = call_pnl
st.session_state["put_pnl"] = put_pnl
        




    


