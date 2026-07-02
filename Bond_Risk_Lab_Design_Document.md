# Bond Risk Lab: Gamified Simulation Platform Design

This document details the business concept, gamification mechanics, scenario catalog, and financial projections for **Bond Risk Lab** – a simulation-based training platform for fixed income risk analysts.

---

## 1. Business Concept Note

### Problem
Fixed income training is historically dry and textbook-based. Junior quants and treasury desk hires struggle to translate mathematical definitions (like Macaulay duration and convexity) into split-second trading decisions. Mistakes are costly; a miscalculated portfolio DV01 can result in millions of dollars of unexpected P&L losses during sudden rate shocks.

### Solution
**Bond Risk Lab** is an interactive, scenario-driven simulation platform. It puts analysts in the hot seat of a virtual treasury desk. The system feeds real-world yield curves and portfolio data, requesting immediate rebalancing and hedging decisions under simulated macroeconomic events.

### Target Audience
1.  **Investment Banks & Asset Managers**: For onboarding new fixed-income analysts and traders.
2.  **Corporate Treasuries**: To train treasury personnel on cash and risk management.
3.  **Business Schools & Quantitative Finance Programs**: As a premium lab component to enhance student employment readiness.

### Differentiation
Unlike standard paper-trading tools, Bond Risk Lab incorporates high-precision pricing engines, multi-factor Monte Carlo simulations, and ML-based sensitivity analytics, matching the exact quantitative engines used by top investment desks.

---

## 2. 1000-Point Scoring Rubric

The simulation scores analysts across six key dimensions, totaling 1,000 points.

| Dimension | Max Points | Description |
| :--- | :--- | :--- |
| **Pricing Accuracy** | 200 | Error tolerance against analytical price calculation. |
| **Hedging Efficiency** | 200 | Minimization of net portfolio DV01 under parallel rate shocks. |
| **Curve Risk Management** | 200 | Mitigation of twist and butterfly curvature risks using KRD. |
| **Risk-Adjusted Return** | 150 | Maximization of yield-to-maturity relative to portfolio VaR. |
| **Speed & Execution** | 150 | Response time to macroeconomic news and transaction costs. |
| **Compliance & Limits** | 100 | Adherence to rating limits, sector concentration, and VaR boundaries. |

---

## 3. Scenario Catalog (20 Distinct Scenarios)

The curriculum is structured into 5 progressive levels.

### Level 1: Foundational (1-200 Points)
1.  **Scenario 01: The Par Yield Curve**: Price a baseline G-Sec portfolio with a flat yield curve.
2.  **Scenario 02: T-Bill Auction**: Hedge a short-term liquidity requirement using 91-day and 364-day bills.
3.  **Scenario 03: The Linear Fallacy**: Experience why duration-only pricing fails under a large 200bps rate cut.
4.  **Scenario 04: Corporate Spread Widen**: Manage a portfolio during a sudden credit rating downgrade of a major corporate sector.

### Level 2: Intermediate (201-400 Points)
5.  **Scenario 05: RBI Repo surprise**: Rebalance a portfolio within 5 minutes of a surprise 25bps repo rate cut.
6.  **Scenario 06: Operation Twist**: Adjust portfolio duration as the RBI buys long-end and sells short-end bonds.
7.  **Scenario 07: SDL Spread Arbitrage**: Capitalize on wider-than-usual spreads of State Development Loans.
8.  **Scenario 08: The MBS Prepayment trap**: Hedge a portfolio of mortgage-backed securities experiencing negative convexity.

### Level 3: Advanced (401-600 Points)
9.  **Scenario 09: Steepener Shock**: Hedge a portfolio against a steepening curve (short rates down, long rates up).
10. **Scenario 10: The Belly Hump**: Manage curvature risk during a massive butterfly yield curve shift.
11. **Scenario 11: Monte Carlo Stress Test**: Calibrate parallel volatility to match a historical 99% VaR limit.
12. **Scenario 12: Credit Default Swaps**: Purchase protection for corporate exposures during a systemic banking crisis.

### Level 4: Expert (601-800 Points)
13. **Scenario 13: SVB Reenactment**: Manage a high-concentration long-duration portfolio during rapid interest rate hikes.
14. **Scenario 14: Multi-Factor VaR Limit**: Allocate weights across 300 bonds to stay within a 3-factor CVaR limit.
15. **Scenario 15: Nelson-Siegel Arbitrage**: Identify mispriced bonds deviating from the fitted yield curve.
16. **Scenario 16: Machine Learning Alpha**: Use Random Forest pricing to execute high-frequency arbitrage trades.

### Level 5: Master (801-1000 Points)
17. **Scenario 17: Sovereign Debt Crisis**: Hedge European sovereign bonds during a debt restructuring.
18. **Scenario 18: Zero-Coupon Bootstrap**: Reconstruct the spot curve from illiquid corporate bonds.
19. **Scenario 19: The Liquidity Freeze**: Rebalance a portfolio when bid-ask spreads widen by 150bps.
20. **Scenario 20: Hyper-Inflation**: Protect a multi-currency pension fund from hyper-inflationary curve twists.

---

## 4. Achievement Badges (10 Badges)

1.  **First Coupon**: Complete your first bond pricing scenario.
2.  **Excel Wizard**: Replicate the pricing engine in Excel with 0 errors.
3.  **Duration Master**: Successfully hedge all parallel risk in a portfolio.
4.  **Convexity King**: Generate positive P&L from a volatile rate environment using long-end bonds.
5.  **Cholesky Warrior**: Calibrate a 3-factor Monte Carlo simulation engine.
6.  **Svensson Explorer**: Fit the yield curve with an $R^2 > 0.999$.
7.  **Neural Pioneer**: Build a Neural Network model that out-performs tree models.
8.  **SVB Survivor**: Successfully hedge a long-duration portfolio during a 500bps rate hike cycle.
9.  **KRD Sniper**: Eliminate all key rate duration mismatches.
10. **Treasury Desk Lead**: Achieve a total score of 950+ points in the Master Level.

---

## 5. Five-Year Revenue Projections (INR Crores)

### Pricing Tiers
1.  **Starter (Academic)**: INR 1.5 Lakhs / year / institution (Up to 100 students).
2.  **Professional (Treasury Desk)**: INR 12 Lakhs / year / desk (Up to 10 users).
3.  **Enterprise (Institutional)**: INR 45 Lakhs / year (Unlimited users, custom scenarios).

### Financial Projections (INR Crores)

| Category | Year 1 | Year 2 | Year 3 | Year 4 | Year 5 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Academic Revenue** | 0.45 | 1.20 | 2.50 | 4.80 | 8.50 |
| **Desk Revenue** | 1.20 | 3.60 | 7.20 | 12.50 | 21.00 |
| **Enterprise Revenue** | 0.90 | 2.70 | 5.40 | 10.80 | 18.00 |
| **Total Revenue** | **2.55** | **7.50** | **15.10** | **28.10** | **47.50** |
| **Operating Costs** | 1.80 | 3.20 | 5.50 | 8.80 | 12.50 |
| **Net Profit** | **0.75** | **4.30** | **9.60** | **19.30** | **35.00** |
