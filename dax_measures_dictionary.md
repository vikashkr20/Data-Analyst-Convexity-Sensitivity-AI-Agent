# Power BI DAX Measures Dictionary & Data Model (MatRisk AI)

This document provides the technical design, star schema relationships, page layouts, and the exact DAX formulas for the **Convexity Sensitivity & Fixed Income Risk Analytics Dashboard**.

---

## 1. Star Schema Data Model

The data model is structured as a star schema to optimize query performance and ensure clear, one-to-many relationships.

### Tables
1.  **Bonds (Fact Table)**: Loaded from `bond_portfolio_krd.csv`. Contains bond-level characteristics, portfolio weights, and calculated KRD vectors.
2.  **DimRating (Dimension)**: Distinct list of credit ratings. Relationship: `DimRating[CreditRating] 1 -> * Bonds[CreditRating]` (Single filter direction).
3.  **DimSector (Dimension)**: Distinct list of sectors. Relationship: `DimSector[Sector] 1 -> * Bonds[Sector]` (Single filter direction).
4.  **DimCurrency (Dimension)**: Distinct list of currencies. Relationship: `DimCurrency[Currency] 1 -> * Bonds[Currency]` (Single filter direction).
5.  **DimTenor (Dimension)**: Tenor buckets (3M, 6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y).
6.  **MCScenarios (Fact Table)**: Loaded from `monte_carlo_results.csv`. Contains 1,000 scenarios of parallel shifts and simulated P&L.
7.  **YieldCurve (Fact/Dim)**: Loaded from `yield_curve_fit_results.csv` showing tenors, actual yields, and fitted NS/Svensson yields.

---

## 2. DAX Measures Dictionary (40+ Measures)

Measures are organized into logical display folders in Power BI.

### Folder: 01. Portfolio Aggregates

1.  **Total MV (INR)**
    ```dax
    Total MV (INR) = SUM(Bonds[MarketValue_INR])
    ```
2.  **Total Quantity**
    ```dax
    Total Quantity = SUM(Bonds[Quantity])
    ```
3.  **Portfolio Weight Check**
    ```dax
    Portfolio Weight Check = SUM(Bonds[PortfolioWeight])
    ```
4.  **Portfolio Macaulay Duration**
    ```dax
    Portfolio MacDur = SUMX(Bonds, Bonds[MacaulayDuration] * Bonds[PortfolioWeight])
    ```
5.  **Portfolio Modified Duration**
    ```dax
    Portfolio ModDur = SUMX(Bonds, Bonds[ModifiedDuration] * Bonds[PortfolioWeight])
    ```
6.  **Portfolio Convexity**
    ```dax
    Portfolio Convexity = SUMX(Bonds, Bonds[Convexity] * Bonds[PortfolioWeight])
    ```
7.  **Portfolio Total DV01**
    ```dax
    Portfolio Total DV01 = SUMX(Bonds, Bonds[DV01_Per100Face] * Bonds[Quantity] / 100)
    ```
8.  **Weighted Average YTM**
    ```dax
    Weighted YTM = SUMX(Bonds, Bonds[YieldToMaturity] * Bonds[PortfolioWeight])
    ```
9.  **Weighted Average Coupon**
    ```dax
    Weighted Coupon = SUMX(Bonds, Bonds[CouponRate] * Bonds[PortfolioWeight])
    ```

### Folder: 02. Risk Contribution Analysis

10. **Duration Contribution**
    ```dax
    Duration Contribution = SUMX(Bonds, Bonds[ModifiedDuration] * Bonds[PortfolioWeight])
    ```
11. **Duration Contribution %**
    ```dax
    Duration Contribution % = DIVIDE([Duration Contribution], CALCULATE([Portfolio ModDur], ALL(Bonds)), 0)
    ```
12. **Convexity Contribution**
    ```dax
    Convexity Contribution = SUMX(Bonds, Bonds[Convexity] * Bonds[PortfolioWeight])
    ```
13. **Convexity Contribution %**
    ```dax
    Convexity Contribution % = DIVIDE([Convexity Contribution], CALCULATE([Portfolio Convexity], ALL(Bonds)), 0)
    ```
14. **DV01 Contribution**
    ```dax
    DV01 Contribution = SUMX(Bonds, Bonds[DV01_Per100Face] * Bonds[Quantity] / 100)
    ```
15. **DV01 Contribution %**
    ```dax
    DV01 Contribution % = DIVIDE([DV01_Contribution], CALCULATE([Portfolio Total DV01], ALL(Bonds)), 0)
    ```

### Folder: 03. Key Rate Duration (KRD)

16. **KRD 3M**
    ```dax
    KRD 3M = SUMX(Bonds, Bonds[KRD_3M] * Bonds[PortfolioWeight])
    ```
17. **KRD 6M**
    ```dax
    KRD 6M = SUMX(Bonds, Bonds[KRD_6M] * Bonds[PortfolioWeight])
    ```
18. **KRD 1Y**
    ```dax
    KRD 1Y = SUMX(Bonds, Bonds[KRD_1Y] * Bonds[PortfolioWeight])
    ```
19. **KRD 2Y**
    ```dax
    KRD 2Y = SUMX(Bonds, Bonds[KRD_2Y] * Bonds[PortfolioWeight])
    ```
20. **KRD 3Y**
    ```dax
    KRD 3Y = SUMX(Bonds, Bonds[KRD_3Y] * Bonds[PortfolioWeight])
    ```
21. **KRD 5Y**
    ```dax
    KRD 5Y = SUMX(Bonds, Bonds[KRD_5Y] * Bonds[PortfolioWeight])
    ```
22. **KRD 7Y**
    ```dax
    KRD 7Y = SUMX(Bonds, Bonds[KRD_7Y] * Bonds[PortfolioWeight])
    ```
23. **KRD 10Y**
    ```dax
    KRD 10Y = SUMX(Bonds, Bonds[KRD_10Y] * Bonds[PortfolioWeight])
    ```
24. **KRD 20Y**
    ```dax
    KRD 20Y = SUMX(Bonds, Bonds[KRD_20Y] * Bonds[PortfolioWeight])
    ```
25. **KRD 30Y**
    ```dax
    KRD 30Y = SUMX(Bonds, Bonds[KRD_30Y] * Bonds[PortfolioWeight])
    ```
26. **Sum of KRDs**
    ```dax
    Sum of KRDs = [KRD 3M] + [KRD 6M] + [KRD 1Y] + [KRD 2Y] + [KRD 3Y] + [KRD 5Y] + [KRD 7Y] + [KRD 10Y] + [KRD 20Y] + [KRD 30Y]
    ```

### Folder: 04. What-If Scenario Analysis
*Requires a What-If parameter table `Yield_Shift_bps` with column `[Yield Shift (bps)]` from -300 to +300.*

27. **What-If dy (decimal)**
    ```dax
    What-If dy = SELECTEDVALUE('Yield_Shift_bps'[Yield Shift (bps)], 0) / 10000
    ```
28. **Scenario P&L (Duration Effect)**
    ```dax
    Scenario PnL Duration = -[Portfolio ModDur] * [What-If dy] * [Total MV (INR)]
    ```
29. **Scenario P&L (Convexity Effect)**
    ```dax
    Scenario PnL Convexity = 0.5 * [Portfolio Convexity] * POWER([What-If dy], 2) * [Total MV (INR)]
    ```
30. **Scenario P&L (Total)**
    ```dax
    Scenario PnL Total = [Scenario PnL Duration] + [Scenario PnL Convexity]
    ```
31. **Convexity Benefit (INR)**
    ```dax
    Convexity Benefit = [Scenario PnL Convexity]
    ```
32. **Convexity Benefit %**
    ```dax
    Convexity Benefit % = DIVIDE([Convexity Benefit], ABS([Scenario PnL Duration]), 0)
    ```

### Folder: 05. Monte Carlo Risk Metrics

33. **VaR 95% (INR)**
    ```dax
    VaR 95% = PERCENTILEX.INC(MCScenarios, MCScenarios[PnL_Total_INR], 0.05)
    ```
34. **VaR 99% (INR)**
    ```dax
    VaR 99% = PERCENTILEX.INC(MCScenarios, MCScenarios[PnL_Total_INR], 0.01)
    ```
35. **CVaR 95% (INR)**
    ```dax
    CVaR 95% = 
    VAR V95 = [VaR 95%]
    RETURN
    CALCULATE(
        AVERAGE(MCScenarios[PnL_Total_INR]),
        FILTER(MCScenarios, MCScenarios[PnL_Total_INR] <= V95)
    )
    ```
36. **CVaR 99% (INR)**
    ```dax
    CVaR 99% = 
    VAR V99 = [VaR 99%]
    RETURN
    CALCULATE(
        AVERAGE(MCScenarios[PnL_Total_INR]),
        FILTER(MCScenarios, MCScenarios[PnL_Total_INR] <= V99)
    )
    ```
37. **Max Simulated Loss**
    ```dax
    Max Simulated Loss = MIN(MCScenarios[PnL_Total_INR])
    ```
38. **Max Simulated Gain**
    ```dax
    Max Simulated Gain = MAX(MCScenarios[PnL_Total_INR])
    ```

### Folder: 06. Yield Curve Fit Diagnostics

39. **Nelson-Siegel Fit R²**
    ```dax
    NS Fit R2 = 
    VAR MeanActual = AVERAGEX(YieldCurve, YieldCurve[ActualYield])
    VAR SS_Tot = SUMX(YieldCurve, POWER(YieldCurve[ActualYield] - MeanActual, 2))
    VAR SS_Res = SUMX(YieldCurve, POWER(YieldCurve[ActualYield] - YieldCurve[NS_Fitted], 2))
    RETURN 1 - DIVIDE(SS_Res, SS_Tot, 0)
    ```
40. **Svensson Fit R²**
    ```dax
    SV Fit R2 = 
    VAR MeanActual = AVERAGEX(YieldCurve, YieldCurve[ActualYield])
    VAR SS_Tot = SUMX(YieldCurve, POWER(YieldCurve[ActualYield] - MeanActual, 2))
    VAR SS_Res = SUMX(YieldCurve, POWER(YieldCurve[ActualYield] - YieldCurve[SV_Fitted], 2))
    RETURN 1 - DIVIDE(SS_Res, SS_Tot, 0)
    ```

---

## 3. Dashboard Layout & Page Design (8 Pages)

### Page 1: Executive Summary
*   **KPI Cards**: Total MV (INR), Portfolio Modified Duration, Portfolio Convexity, Portfolio Total DV01.
*   **Visuals**:
    *   Donut Chart: Portfolio MV by Credit Rating.
    *   Donut Chart: Portfolio MV by Sector.
    *   Table: Top 10 Bonds by Market Value Weight.

### Page 2: Duration Contribution
*   **Visuals**:
    *   Bar Chart: Duration Contribution % by Credit Rating.
    *   Bar Chart: Duration Contribution % by Sector.
    *   Stacked Bar Chart: Duration Contribution by Currency.

### Page 3: Key Rate Duration Heatmap
*   **Visuals**:
    *   Matrix Heatmap: Rows = CreditRating, Columns = KeyRateBucket, Values = [Duration Contribution] (Conditional formatted as a color scale).
    *   Column Chart: Sum of KRDs vs. Portfolio ModDur across Tenors.

### Page 4: Yield Curve Evolution & Fitting
*   **Visuals**:
    *   Line Chart: X = Tenor, Y = ActualYield, NS_Fitted, SV_Fitted (Overlay chart).
    *   KPI Cards: NS R² and SV R² to show fit quality.
    *   Table: Implied Forward Rates.

### Page 5: Monte Carlo P&L Distribution
*   **Visuals**:
    *   Histogram (Column chart): X = P&L buckets (INR Millions), Y = Scenario Count.
    *   Reference Lines: Constant vertical lines indicating 95% VaR and 99% VaR.

### Page 6: VaR/CVaR Monitor
*   **Visuals**:
    *   KPI Cards: 95% VaR, 95% CVaR, 99% VaR, 99% CVaR.
    *   Table: Worst 20 Monte Carlo Scenarios.

### Page 7: ML Model Comparison
*   **Visuals**:
    *   Grouped Column Chart: RMSE, MAE, R² by ML Model (Random Forest, XGBoost, Neural Network).
    *   Scatter Plot: ML-Predicted Price Change vs. Analytical Price Change across shifts.

### Page 8: What-If Scenario Analysis
*   **Visuals**:
    *   Slicer: What-If Yield Shift Slider (-300bps to +300bps).
    *   Gauges: Total P&L Impact, Duration P&L, Convexity Benefit.
    *   Line Chart: Dynamic P&L Sensitivity Curve updating in real-time as the slider moves.

---

## 4. Bookmarks & Guided Narrative Setup

1.  **Bookmark "Base Case"**: Sets Yield Shift parameter to 0 bps.
2.  **Bookmark "RBI Rate Cut Scenario (-50bps)"**: Sets Yield Shift parameter to -50 bps.
3.  **Bookmark "Hawkish Stance Shock (+100bps)"**: Sets Yield Shift parameter to +100 bps.
4.  **Bookmark "Extreme Stress Test (+200bps)"**: Sets Yield Shift parameter to +200 bps.
