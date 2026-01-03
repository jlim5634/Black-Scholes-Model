import math
from scipy.stats import norm
#core math logic program
#foundation of project

class BlackScholes:
    def __init__(
            self, 
            time_to_maturity: float,
            strike: float,
            current_price: float,
            volatility: float,
            interest_rate: float,
    ):
        self.time_to_maturity = time_to_maturity
        self.strike = strike
        self.current_price = current_price
        self.volatility = volatility
        self.interest_rate = interest_rate

#cummulative distrubition funct for variable. Black-Scholes depends on probabilities

    def run(
        self,
    ):
        time_to_maturity = self.time_to_maturity
        strike = self.strike
        current_price = self.current_price
        volatility = self.volatility
        interest_rate = self.interest_rate

        d1 = (
            math.log(current_price/strike) +
            (interest_rate + 0.5 * volatility ** 2) * time_to_maturity
            )/(
                volatility * math.sqrt(time_to_maturity)

            )
        d2 = d1 - volatility * math.sqrt(time_to_maturity)

        call_price = current_price * norm.cdf(d1) - (
            strike * math.exp(-(interest_rate * time_to_maturity)) * norm.cdf(d2)
        )

        put_price = (
            strike * math.exp(-(interest_rate * time_to_maturity)) * norm.cdf(-d2)
        ) - current_price *norm.cdf(-d1)
        
        self.call_price = call_price
        self.put_price = put_price

        self.call_delta = norm.cdf(d1)
        self.put_delta = 1 - norm.cdf(d1)

        self.call_gamma = norm.pdf(d1) / (
            current_price * volatility * math.sqrt(time_to_maturity)
        )

        self.put_gamma = self.call_gamma

        return call_price, put_price

if __name__ == "__main__":
    time_to_maturity = 2
    strike = 90
    current_price = 100
    volatility = 0.2
    interest_rate = 0.05

    BS = BlackScholes(
        time_to_maturity=time_to_maturity,
        strike=strike,
        current_price=current_price,
        volatility=volatility,
        interest_rate=interest_rate
    )

    BS.run()

    print(f"Call Price: {BS.call_price:.2f}")
    print(f"Put Price: {BS.put_price:.2f}")
    print(f"Call Delta: {BS.call_delta:.4f}")
    print(f"Put Delta: {BS.put_delta:.4f}")
    print(f"Call Gamma: {BS.call_gamma:.4f}")
    print(f"Put Gamma: {BS.put_gamma:.4f}")



