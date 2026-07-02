import numpy as np
import scipy.stats as stats

def kupiec_pof_test(n_observations, n_failures, confidence=0.95):
    """
    Performs the Kupiec Proportion of Failure (POF) Likelihood Ratio test.
    Ho: The VaR model is accurate (the failure rate equals 1 - confidence).
    """
    p = 1.0 - confidence
    if n_failures == 0:
        # Avoid division by zero in log
        # Log-likelihood ratio limit as failures -> 0
        lr = -2 * ((n_observations) * math.log(1 - p) - (n_observations) * math.log(1.0)) # simplified
        # Better: use standard formula but prevent log(0)
        n_failures = 1e-10
        
    # Empirical failure rate
    p_hat = n_failures / n_observations
    
    # Kupiec LR statistic formula:
    # LR = -2 * ln( ( (1 - p)**(N - x) * p**x ) / ( (1 - p_hat)**(N - x) * p_hat**x ) )
    # using log terms for stability:
    term_null = (n_observations - n_failures) * np.log(1.0 - p) + n_failures * np.log(p)
    
    # Avoid log(0) if p_hat is 0 or 1
    p_hat_adj = max(1e-10, min(p_hat, 1.0 - 1e-10))
    term_alt = (n_observations - n_failures) * np.log(1.0 - p_hat_adj) + n_failures * np.log(p_hat_adj)
    
    lr_stat = -2 * (term_null - term_alt)
    
    # Chi-square p-value with 1 degree of freedom
    p_value = 1.0 - stats.chi2.cdf(lr_stat, df=1)
    
    # Rejection decision (at 5% significance level, critical value is 3.841)
    rejected = lr_stat > 3.841
    
    return {
        "LR_Statistic": lr_stat,
        "P_Value": p_value,
        "Rejected": rejected,
        "Expected_Failures": n_observations * p,
        "Actual_Failures": int(n_failures) if n_failures >= 1 else 0
    }

def run_backtest_demo():
    print("=" * 60)
    print("DAY 14 DELIVERABLE: VaR BACKTESTING (KUPIEC POF TEST)")
    print("=" * 60)
    
    # Let's test 250 days of historical portfolio returns
    np.random.seed(101)
    n_days = 250
    p = 0.05 # 95% VaR
    
    # Generate mock daily portfolio P&L
    daily_pnl = np.random.normal(5000, 600000, n_days)
    
    # Mock daily 95% VaR (constant or rolling, let's say constant at -987,000 INR)
    # Typically VaR is a negative number representing the maximum loss
    daily_var = np.full(n_days, -987000.0)
    
    # Count breaches (where P&L is negative and exceeds VaR in magnitude, i.e. P&L <= VaR)
    breaches = np.sum(daily_pnl <= daily_var)
    
    print(f"Backtest Period:      {n_days} Trading Days")
    print(f"VaR Confidence Level: 95.0%")
    print(f"Expected Breaches:    {n_days * p:.1f}")
    print(f"Actual Breaches:      {breaches}")
    
    res = kupiec_pof_test(n_days, breaches, confidence=0.95)
    print("-" * 60)
    print(f"Kupiec LR Statistic:  {res['LR_Statistic']:.4f} (Critical Value: 3.841)")
    print(f"Chi-Square P-Value:   {res['P_Value']:.4f}")
    print(f"Model Rejected?       {res['Rejected']}")
    print("-" * 60)
    
    if res['Rejected']:
        print("RESULT: Reject Ho. The VaR model is statistically inaccurate at the 5% level.")
    else:
        print("RESULT: Fail to reject Ho. The VaR model is statistically valid.")
    print("=" * 60)

if __name__ == "__main__":
    run_backtest_demo()
