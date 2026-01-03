import math
from scipy.stats import norm

#core math logic program
#foundation of project


# theta(time decay)
# vega (volatility sensitivity)
# delta (price sensitivity)
# gamma (delta's sensitivity)
# rho (sensitivity of option price to interest rate) small bc intererest rate moves slow

class BlackScholes:
    def __init__(
            self, 
            time_to_maturity: float,
            strike: float,
            current_price: float,
            volatility: float,
            interest_rate: float,
    ):
        if time_to_maturity <= 0:
            raise ValueError("Time to maturity must be positive")
        self.T = time_to_maturity
        self.K = strike
        self.S = current_price
        self.sigma = volatility
        self.r = interest_rate
    
    def d1(self): #expected benefit of receiving the stock. Indicates how much option price changes for $1 change in stock price
        return (
            math.log(self.S/self.K) +
            (self.r + 0.5 * self.sigma ** 2) * self.T
            ) / (self.sigma * math.sqrt(self.T))
    
    def d2(self): #probaility of exercising the option. Risk-neutral prob that the option will expire in-the-money
        return self.d1() - self.sigma * math.sqrt(self.T)
    
    def price(self):
        d1 = self.d1()
        d2 = self.d2()

        call = self.S * norm.cdf(d1) - (
            self.K * math.exp(-(self.r * self.T)) * norm.cdf(d2)
        )

        put = (
            self.K * math.exp(-(self.r * self.T)) * norm.cdf(-d2)
        ) - self.S * norm.cdf(-d1)

        return call, put

    def greeks(self):
        d1 = self.d1()
        d2 = self.d2()

        pdf_d1 = norm.pdf(d1)

        call_delta = norm.cdf(d1)
        put_delta = norm.cdf(d1) - 1


        gamma = pdf_d1 / (
            self.S * self.sigma * math.sqrt(self.T)
        )

        vega = self.S * pdf_d1 * math.sqrt(self.T)
        vega /= 100 #to report 1% in change in volatility

        call_theta = (
            -(self.S * pdf_d1 * self.sigma) / (2 * math.sqrt(self.T))
            - self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(d2)
        )

        put_theta = (
            - (self.S * pdf_d1 * self.sigma) / (2 * math.sqrt(self.T))
            + self.r * self.K * math.exp(-self.r * self.T) * norm.cdf(-d2)
        )

        call_rho = self.K * self.T * math.exp(-self.r * self.T) * norm.cdf(d2)
        put_rho = -self.K * self.T * math.exp(-self.r * self.T) * norm.cdf(-d2)

        return {
            "call_delta": call_delta,
            "put_delta": put_delta,
            "gamma": gamma,
            "vega": vega,
            "call_theta": call_theta,
            "put_theta": put_theta,
            "call_rho": call_rho,
            "put_rho": put_rho
        }


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

    call_price, put_price = BS.price()

    greeks = BS.greeks()

    print(f"Call Price: {call_price:.2f}")
    print(f"Put Price: {put_price:.2f}")
    print(f"Call Delta: {greeks['call_delta']:.4f}")
    print(f"Put Delta: {greeks['put_delta']:.4f}")
    print(f"Gamma: {greeks['gamma']:.4f}")
    print(f"Vega: {greeks['vega']:.4f}")
    print(f"Call Theta: {greeks['call_theta']:.4f}")
    print(f"Put Theta: {greeks['put_theta']:.4f}")
    print(f"Call Rho: {greeks['call_rho']:.4f}")
    print(f"Put Rho: {greeks['put_rho']:.4f}")



