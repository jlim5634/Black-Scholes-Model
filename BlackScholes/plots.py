#takes numbers and produces plots but does not compute prices itself
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns #helps provide high-lvl UI for stats graphics
from BlackScholes import BlackScholes #import class
import plotly.graph_objects as go

class Plots:
    def __init__(self):
        pass #just generates plots so can be stateless

    def plot_call_vs_volatility(S,K,T,r, volatility_range=None):
        if volatility_range is None:
            volatility_range = np.linspace(0.05, 0.6, 50)        
        prices = []

        for sigma in volatility_range:
            bs = BlackScholes(time_to_maturity=T, strike=K, current_price=S, volatility = sigma, interest_rate=r)
            call_price, _ = bs.price()
            prices.append(call_price)

        fig, ax = plt.subplots()
        ax.plot(volatility_range, prices)
        ax.set_xlabel("Volatility")
        ax.set_ylabel("Call Price")
        ax.set_title("Call Price vs Volatility")
        return fig

    def generate_price_grid(self, bs_model, spot_range, vol_range):
        #create grid of call and put prices across spot and volatility. Returns two 2d arrays (call and put)
        
        #default ranges if none provided
        if spot_range is None:
            spot_range = np.linspace(bs_model.S * 0.8, bs_model.S * 1.2, 20)
        if vol_range is None:
            vol_range = np.linspace(0.1, 0.5, 10)

        call_prices = np.zeros((len(vol_range), len(spot_range)))
        put_prices = np.zeros((len(vol_range), len(spot_range)))

        for i, vol in enumerate(vol_range):
            for j, spot in enumerate(spot_range):
                bs_temp = BlackScholes(time_to_maturity=bs_model.T, strike=bs_model.K, current_price=spot, volatility = vol, interest_rate=bs_model.r)
                call_price, put_price = bs_temp.price()
                call_prices[i,j] = call_price
                put_prices[i,j] = put_price
        return call_prices, put_prices

    def plot_call_heatmap(self, call_prices, spot_range, vol_range):
        fig, ax = plt.subplots(figsize=(10,8))
        sns.heatmap(call_prices, xticklabels=np.round(spot_range, 2),
                    yticklabels=np.round(vol_range, 2),
                    annot=True, fmt=".2f", cmap="viridis", ax=ax) #show 2 decimals
        ax.set_title('Call Price Heatmap')
        ax.set_xlabel('Spot Price ($)')
        ax.set_ylabel('Volatility σ)')
        return fig
    
    def plot_put_heatmap(self, put_prices, spot_range, vol_range):
        fig, ax = plt.subplots(figsize=(10,8))
        sns.heatmap(put_prices, xticklabels=np.round(spot_range, 2),
                    yticklabels=np.round(vol_range, 2),
                    annot=True, fmt=".2f", cmap="viridis", ax=ax)
        ax.set_title('Put Price Heatmap')
        ax.set_xlabel('Spot Price ($)')
        ax.set_ylabel('Volatility (σ)')
        return fig

    def plot_call_surface(self, call_prices, spot_range, vol_range):
        #3d surface plot for call prices
        fig = go.Figure(data=[go.Surface(
            z = call_prices,
            x = spot_range,
            y = vol_range,
            colorscale="Viridis"
        )])
        fig.update_layout(
            title='Call Price Surface',
            scene=dict(
                xaxis_title='Spot Price ($)',
                yaxis_title='Volatility σ)',
                zaxis_title='Call Price ($)'
            ),
            autosize=True,
        )
        return fig
    
    def plot_put_surface(self, put_prices, spot_range, vol_range):
        #3d surface plot for put prices
        fig = go.Figure(data=[go.Surface(
            z = put_prices,
            x = spot_range,
            y = vol_range,
            colorscale="Viridis"
        )])
        fig.update_layout(
            title='Put Price Surface',
            scene=dict(
                xaxis_title='Spot Price ($)',
                yaxis_title='Volatility (σ)',
                zaxis_title='Put Price ($)'
            ),
            autosize=True,
        )
        return fig