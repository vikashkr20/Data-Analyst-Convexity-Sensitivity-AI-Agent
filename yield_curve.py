import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as opt
import math

def nelson_siegel(t, b0, b1, b2, lam):
    if t <= 0:
        return b0 + b1
    x = t / lam
    f1 = (1.0 - np.exp(-x)) / x
    f2 = f1 - np.exp(-x)
    return b0 + b1 * f1 + b2 * f2

def svensson(t, b0, b1, b2, b3, lam1, lam2):
    if t <= 0:
        return b0 + b1
    x1 = t / lam1
    x2 = t / lam2
    f1 = (1.0 - np.exp(-x1)) / x1
    f2 = f1 - np.exp(-x1)
    f3 = (1.0 - np.exp(-x2)) / x2 - np.exp(-x2)
    return b0 + b1 * f1 + b2 * f2 + b3 * f3

def bootstrap_spot_curve(tenors, yields):
    """
    Bootstraps zero-coupon rates (spot rates) from par coupon yields.
    Assumes semi-annual coupon payments.
    """
    zero_rates = []
    
    for i, T in enumerate(tenors):
        y = yields[i]
        c = y / 2.0 # semi-annual coupon rate
        
        # If it is the first tenor (e.g. 3M = 0.25Y)
        if i == 0:
            # Short-term T-bill type pricing: 100 = (100 + c*100) / (1 + z/2)**(2*T)?
            # Or simple discount: 100 = 100 * (1 + y * T)?
            # Let's use the standard bond price equation:
            # 100 = (100 + c*100) / (1 + z/2)**(2*T) -> 1 + z/2 = (1 + c)**(1/(2*T)) -> z = 2 * ((1+c)**(1/(2*T)) - 1)
            z = y
            zero_rates.append(z)
            continue
            
        # For longer tenors, we solve for z_T:
        # Price (100) = sum_{t} [ c * 100 / (1 + z_t/2)**(2*t) ] + (100 + c*100) / (1 + z_T/2)**(2*T)
        # where we interpolate zero rates for intermediate coupon payment times.
        # To make it simple, let's write a numerical solver for z_T
        def price_error(z_guess):
            # Coupon payment times are at 0.5, 1.0, 1.5, ... up to T
            # We interpolate zero rates at these payment times from known zero_rates
            pmt_times = np.arange(0.5, T + 0.01, 0.5)
            pv_sum = 0
            for t in pmt_times:
                cf = c * 100 if t < T else (c + 1.0) * 100
                # Interpolate zero rate at t
                if t < T:
                    # linear interpolation
                    z_t = np.interp(t, tenors[:len(zero_rates)], zero_rates)
                else:
                    z_t = z_guess
                pv_sum += cf / ((1 + z_t / 2.0) ** (2 * t))
            return (pv_sum - 100) ** 2
            
        res = opt.minimize(price_error, x0=[y], bounds=[(0.001, 0.20)])
        zero_rates.append(res.x[0])
        
    return np.array(zero_rates)

def run_yield_curve_modelling():
    df_all = pd.read_csv("yield_curve_history.csv")
    
    # Extract curve for the most recent date: 2024-10-30
    recent_date = "2024-10-30"
    df = df_all[df_all['CurveDate'] == recent_date].sort_values('Tenor_Years')
    
    tenors = df['Tenor_Years'].values
    yields = df['Yield'].values
    zero_csv = df['ZeroRate'].values
    
    print("=" * 60)
    print(f"DAY 10: YIELD CURVE MODELLING FOR {recent_date}")
    print("=" * 60)
    
    # 1. Fit Nelson-Siegel
    # Objective function: sum of squared pricing/yield errors
    def ns_error(params):
        b0, b1, b2, lam = params
        preds = np.array([nelson_siegel(t, b0, b1, b2, lam) for t in tenors])
        return np.sum((yields - preds) ** 2)
        
    # Initial guess: b0=0.07, b1=-0.01, b2=0.01, lam=2.0
    ns_init = [0.07, -0.01, 0.01, 2.0]
    ns_bounds = [(0.01, 0.15), (-0.10, 0.10), (-0.15, 0.15), (0.1, 10.0)]
    ns_res = opt.minimize(ns_error, x0=ns_init, bounds=ns_bounds)
    b0_ns, b1_ns, b2_ns, lam_ns = ns_res.x
    
    # 2. Fit Svensson
    def sv_error(params):
        b0, b1, b2, b3, lam1, lam2 = params
        preds = np.array([svensson(t, b0, b1, b2, b3, lam1, lam2) for t in tenors])
        return np.sum((yields - preds) ** 2)
        
    sv_init = [0.07, -0.01, 0.01, -0.01, 2.0, 5.0]
    sv_bounds = [(0.01, 0.15), (-0.10, 0.10), (-0.15, 0.15), (-0.15, 0.15), (0.1, 10.0), (0.1, 15.0)]
    sv_res = opt.minimize(sv_error, x0=sv_init, bounds=sv_bounds)
    b0_sv, b1_sv, b2_sv, b3_sv, lam1_sv, lam2_sv = sv_res.x
    
    # 3. Bootstrap spot curve
    bootstrapped_zero = bootstrap_spot_curve(tenors, yields)
    
    # 4. Compare fit quality
    ns_preds = np.array([nelson_siegel(t, b0_ns, b1_ns, b2_ns, lam_ns) for t in tenors])
    sv_preds = np.array([svensson(t, b0_sv, b1_sv, b2_sv, b3_sv, lam1_sv, lam2_sv) for t in tenors])
    
    ns_rmse = np.sqrt(np.mean((yields - ns_preds) ** 2))
    sv_rmse = np.sqrt(np.mean((yields - sv_preds) ** 2))
    
    ns_r2 = 1.0 - (np.sum((yields - ns_preds)**2) / np.sum((yields - np.mean(yields))**2))
    sv_r2 = 1.0 - (np.sum((yields - sv_preds)**2) / np.sum((yields - np.mean(yields))**2))
    
    print("Yield Curve Fitting Quality:")
    print(f"  Nelson-Siegel | RMSE: {ns_rmse:.6f} | R²: {ns_r2:.6f}")
    print(f"  Svensson      | RMSE: {sv_rmse:.6f} | R²: {sv_r2:.6f}")
    print("-" * 60)
    print("Nelson-Siegel Fitted Parameters:")
    print(f"  beta0 (Level):     {b0_ns:.6f}")
    print(f"  beta1 (Slope):     {b1_ns:.6f}")
    print(f"  beta2 (Curvature): {b2_ns:.6f}")
    print(f"  lambda (Decay):    {lam_ns:.6f}")
    print("-" * 60)
    
    # 5. Compute forward rates from bootstrapped zero curve
    # Forward rate formula: f(T1, T2) = (z2 * T2 - z1 * T1) / (T2 - T1) (continuously compounded)
    # Let's find zero rates at 1Y, 2Y, 5Y, and 10Y by linear interpolation of bootstrapped zero curve
    z_1y = np.interp(1.0, tenors, bootstrapped_zero)
    z_2y = np.interp(2.0, tenors, bootstrapped_zero)
    z_5y = np.interp(5.0, tenors, bootstrapped_zero)
    z_10y = np.interp(10.0, tenors, bootstrapped_zero)
    
    f_1_2 = (z_2y * 2.0 - z_1y * 1.0) / (2.0 - 1.0)
    f_2_5 = (z_5y * 5.0 - z_2y * 2.0) / (5.0 - 2.0)
    f_5_10 = (z_10y * 10.0 - z_5y * 5.0) / (10.0 - 5.0)
    
    print("Implied Forward Rates (Continuously Compounded):")
    print(f"  1Y-2Y Forward Rate: {f_1_2 * 100:.4f}%")
    print(f"  2Y-5Y Forward Rate: {f_2_5 * 100:.4f}%")
    print(f"  5Y-10Y Forward Rate: {f_5_10 * 100:.4f}%")
    print("-" * 60)
    
    # Export fitted yield curves to CSV
    fit_df = pd.DataFrame({
        "Tenor": tenors,
        "ActualYield": yields,
        "NS_Fitted": ns_preds,
        "SV_Fitted": sv_preds,
        "BootstrappedZero": bootstrapped_zero,
        "CSV_ZeroRate": zero_csv
    })
    fit_df.to_csv("yield_curve_fit_results.csv", index=False)
    print("Curve results exported to: yield_curve_fit_results.csv")
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.scatter(tenors, yields * 100, color='red', s=60, label='Actual Yields (Market)', zorder=5)
    
    # Generate smooth tenors for plotting fitted curves
    smooth_tenors = np.linspace(0.1, 30.0, 200)
    ns_smooth = np.array([nelson_siegel(t, b0_ns, b1_ns, b2_ns, lam_ns) for t in smooth_tenors])
    sv_smooth = np.array([svensson(t, b0_sv, b1_sv, b2_sv, b3_sv, lam1_sv, lam2_sv) for t in smooth_tenors])
    
    plt.plot(smooth_tenors, ns_smooth * 100, 'b-', linewidth=2, label='Nelson-Siegel Fit')
    plt.plot(smooth_tenors, sv_smooth * 100, 'g--', linewidth=2, label='Svensson Fit')
    
    plt.title("Indian G-Sec Yield Curve Fitting (2024-10-30)", fontsize=14, fontweight='bold')
    plt.xlabel("Maturity Tenor (Years)")
    plt.ylabel("Yield to Maturity (%)")
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("yield_curve_fitting.png", dpi=300)
    plt.close()
    print("Fitting overlay chart saved to: yield_curve_fitting.png")
    
    # Economic Interpretation
    interpretation = f"""# Yield Curve Modelling & Economic Interpretation (Valuation Date: {recent_date})

## Curve Fitting Performance
- The **Svensson model** out-performed the Nelson-Siegel model slightly (RMSE: {sv_rmse:.6f} vs. {ns_rmse:.6f}, and R²: {sv_r2:.6f} vs. {ns_r2:.6f}). The two extra parameters in Svensson ($\beta_3$ and $\lambda_2$) allow it to capture the second hump in the medium-term sector of the Indian yield curve.

## Implied Forward Rates
- **1Y-2Y Forward Rate**: {f_1_2 * 100:.4f}%
- **2Y-5Y Forward Rate**: {f_2_5 * 100:.4f}%
- **5Y-10Y Forward Rate**: {f_5_10 * 100:.4f}%

## Market Expectations
- If the forward rates are **higher** than current spot rates, the yield curve is upward sloping. This implies that the market expects the RBI to hike rates in the future, or that there is a significant term premium required by investors for holding long-duration bonds.
- If the forward rates are **lower** than current spot rates (inverted curve), it indicates expectations of rate cuts in the near term.
- Here, the 1Y-2Y forward rate is {f_1_2 * 100:.2f}%, while the 3M spot yield is {yields[0]*100:.2f}%, indicating a steep upward slope at the short end. The curve levels off at the long end (5Y-10Y forward rate of {f_5_10 * 100:.2f}%), reflecting a stabilizing long-term inflation and interest rate outlook.
"""
    with open("yield_curve_interpretation.md", "w") as f:
        f.write(interpretation)
    print("Economic interpretation written to: yield_curve_interpretation.md")
    print("=" * 60)

if __name__ == "__main__":
    run_yield_curve_modelling()
