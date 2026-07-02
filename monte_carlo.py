import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import scipy.stats as stats
import seaborn as sns
from bond_pricing import bond_price
from key_rate_duration import calculate_krd_vector

def load_data():
    try:
        df = pd.read_csv("bond_portfolio_krd.csv")
    except FileNotFoundError:
        # If KRD file is missing, recreate it
        import subprocess
        subprocess.run(["python", "key_rate_duration.py"], check=True)
        df = pd.read_csv("bond_portfolio_krd.csv")
    return df

# Define factor loadings (Nelson-Siegel style with lambda=2.0)
def get_loadings(t, lam=2.0):
    if t <= 0:
        return 1.0, 1.0, 0.0
    L1 = 1.0
    x = t / lam
    L2 = (1.0 - math.exp(-x)) / x
    L3 = L2 - math.exp(-x)
    return L1, L2, L3

class BondRiskMC:
    def __init__(self, df, n_sims=1000):
        self.df = df
        self.n = n_sims
        self.tenors = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0]
        self.tenor_labels = ['3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
        
    def run_parallel_mc(self, vol_p=0.01):
        """
        Runs Monte Carlo using parallel shifts only (Day 5 requirement).
        """
        np.random.seed(42)
        shocks = np.random.normal(0, vol_p, self.n)
        
        total_mv = self.df['MarketValue_INR'].sum()
        
        # Portfolio aggregates
        if 'Recalc_ModifiedDuration' in self.df.columns:
            port_dur = (self.df['Recalc_ModifiedDuration'] * self.df['PortfolioWeight']).sum()
            port_conv = (self.df['Recalc_Convexity'] * self.df['PortfolioWeight']).sum()
        else:
            port_dur = (self.df['ModifiedDuration'] * self.df['PortfolioWeight']).sum()
            port_conv = (self.df['Convexity'] * self.df['PortfolioWeight']).sum()
            
        pnl_dur_only = []
        pnl_dur_conv = []
        
        for dy in shocks:
            dur_eff = -port_dur * dy * total_mv
            conv_eff = 0.5 * port_conv * (dy**2) * total_mv
            pnl_dur_only.append(dur_eff)
            pnl_dur_conv.append(dur_eff + conv_eff)
            
        return shocks, np.array(pnl_dur_only), np.array(pnl_dur_conv)
        
    def run_3factor_mc(self, vol_p=0.01, vol_t=0.005, vol_b=0.003):
        """
        Runs Monte Carlo using 3 correlated factors: Level, Twist, Butterfly (Day 6 requirement).
        Uses Cholesky decomposition to generate correlated factor shocks.
        """
        np.random.seed(42)
        
        # Correlation matrix
        R = np.array([
            [1.0, -0.3, 0.1],
            [-0.3, 1.0, 0.2],
            [0.1, 0.2, 1.0]
        ])
        
        # Volatility diagonal matrix
        D = np.diag([vol_p, vol_t, vol_b])
        
        # Covariance matrix
        Sigma = D @ R @ D
        
        # Cholesky factor L (lower triangular)
        L = np.linalg.cholesky(Sigma)
        
        # Generate independent standard normal vectors
        Z = np.random.normal(0, 1, size=(3, self.n))
        
        # Correlated shocks: X = L * Z
        X = L @ Z # Shape (3, 1000)
        
        level_shocks = X[0, :]
        twist_shocks = X[1, :]
        bf_shocks = X[2, :]
        
        # Prepare KRD arrays from DataFrame
        krd_cols = [f'KRD_{label}' for label in self.tenor_labels]
        krd_matrix = self.df[krd_cols].values # Shape (301, 10)
        weights = self.df['PortfolioWeight'].values
        portfolio_krd = np.dot(weights, krd_matrix)
        
        total_mv = self.df['MarketValue_INR'].sum()
        
        if 'Recalc_Convexity' in self.df.columns:
            port_conv = (self.df['Recalc_Convexity'] * self.df['PortfolioWeight']).sum()
        else:
            port_conv = (self.df['Convexity'] * self.df['PortfolioWeight']).sum()
            
        pnl_3factor = []
        
        # Precompute tenor factor loadings
        loadings = np.array([get_loadings(t) for t in self.tenors]) # Shape (10, 3)
        # loadings[:, 0] is Level, loadings[:, 1] is Twist, loadings[:, 2] is Curvature
        
        for i in range(self.n):
            # Factors for this scenario
            f_p = level_shocks[i]
            f_t = twist_shocks[i]
            f_b = bf_shocks[i]
            
            # Shock to each tenor point: dy_j = f_p * L1_j + f_t * L2_j + f_b * L3_j
            dy_tenors = f_p * loadings[:, 0] + f_t * loadings[:, 1] + f_b * loadings[:, 2]
            
            # First-order P&L from KRDs
            # P&L_KRD = - sum( KRD_j * dy_j ) * MV
            dur_eff = -np.sum(portfolio_krd * dy_tenors) * total_mv
            
            # Second-order P&L from parallel shift convexity
            # We use the Level factor f_p as the parallel shift component
            conv_eff = 0.5 * port_conv * (f_p**2) * total_mv
            
            pnl_3factor.append(dur_eff + conv_eff)
            
        return level_shocks, twist_shocks, bf_shocks, np.array(pnl_3factor)

def calculate_var_cvar(pnl, confidence=0.95):
    # VaR is the 5th/1st percentile of P&L (since losses are negative, it's a negative value)
    var_val = np.percentile(pnl, (1 - confidence) * 100)
    cvar_val = np.mean(pnl[pnl <= var_val])
    return var_val, cvar_val

def generate_day5_plots(shocks, pnl_dur, pnl_dc, var95, var99):
    sns.set_theme(style="darkgrid")
    
    # Chart 1: P&L Distribution Histogram
    plt.figure(figsize=(10, 6))
    sns.histplot(pnl_dc / 1e6, bins=50, kde=True, color='blue', edgecolor='black', alpha=0.6)
    plt.axvline(var95 / 1e6, color='orange', linestyle='--', linewidth=2, label=f'95% VaR (INR {var95/1e6:.2f}M)')
    plt.axvline(var99 / 1e6, color='red', linestyle='-', linewidth=2, label=f'99% VaR (INR {var99/1e6:.2f}M)')
    plt.title("Monte Carlo P&L Distribution (Day 5: Parallel Shifts)", fontsize=14, fontweight='bold')
    plt.xlabel("Scenario P&L (INR Millions)")
    plt.ylabel("Frequency")
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig("mc_parallel_pnl_dist.png", dpi=300)
    plt.close()
    
    # Chart 2: QQ Plot
    plt.figure(figsize=(8, 6))
    stats.probplot(pnl_dc, dist="norm", plot=plt)
    plt.title("Q-Q Plot of Parallel MC P&L", fontsize=14, fontweight='bold')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("mc_parallel_qq.png", dpi=300)
    plt.close()
    
    # Chart 3: P&L vs Yield Change Scatter
    plt.figure(figsize=(10, 6))
    plt.scatter(shocks * 10000, pnl_dc / 1e6, color='blue', alpha=0.5, label='Duration + Convexity P&L')
    plt.scatter(shocks * 10000, pnl_dur / 1e6, color='red', alpha=0.3, marker='x', label='Duration Only P&L')
    plt.axhline(0, color='black', linewidth=0.8, linestyle=':')
    plt.axvline(0, color='black', linewidth=0.8, linestyle=':')
    plt.title("Scenario P&L vs Yield Change (Parallel MC)", fontsize=14, fontweight='bold')
    plt.xlabel("Yield Curve Shift (basis points)")
    plt.ylabel("P&L (INR Millions)")
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig("mc_parallel_scatter.png", dpi=300)
    plt.close()

def generate_day6_plots(pnl_3f, var95_3f, var99_3f, var_comparison):
    sns.set_theme(style="darkgrid")
    
    # Chart 1: 3-Factor P&L Distribution Histogram
    plt.figure(figsize=(10, 6))
    sns.histplot(pnl_3f / 1e6, bins=50, kde=True, color='darkgreen', edgecolor='black', alpha=0.6)
    plt.axvline(var95_3f / 1e6, color='orange', linestyle='--', linewidth=2, label=f'95% VaR (INR {var95_3f/1e6:.2f}M)')
    plt.axvline(var99_3f / 1e6, color='red', linestyle='-', linewidth=2, label=f'99% VaR (INR {var99_3f/1e6:.2f}M)')
    plt.title("Monte Carlo P&L Distribution (Day 6: 3-Factor Model)", fontsize=14, fontweight='bold')
    plt.xlabel("Scenario P&L (INR Millions)")
    plt.ylabel("Frequency")
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig("mc_3factor_pnl_dist.png", dpi=300)
    plt.close()
    
    # Chart 2: VaR Comparison Bar Chart
    plt.figure(figsize=(8, 6))
    x = np.arange(2)
    width = 0.35
    
    plt.bar(x - width/2, var_comparison['parallel'] / 1e6, width, label='Parallel-Only Model', color='blue')
    plt.bar(x + width/2, var_comparison['3factor'] / 1e6, width, label='3-Factor Model', color='darkgreen')
    
    plt.title("VaR Comparison: Parallel-Only vs. 3-Factor Model", fontsize=14, fontweight='bold')
    plt.xticks(x, ['95% Confidence', '99% Confidence'])
    plt.ylabel("Value-at-Risk (INR Millions, negative means loss)")
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig("mc_var_comparison.png", dpi=300)
    plt.close()

def run_sensitivity_analysis(mc_engine):
    # Day 6 sensitivity analysis: Var vs twist volatility from 3bps to 10bps
    twist_vols = np.linspace(0.0003, 0.0010, 8) # 3bps to 10bps
    var95_list = []
    var99_list = []
    
    for vol_t in twist_vols:
        _, _, _, pnl_3f = mc_engine.run_3factor_mc(vol_p=0.01, vol_t=vol_t, vol_b=0.003)
        var95, _ = calculate_var_cvar(pnl_3f, 0.95)
        var99, _ = calculate_var_cvar(pnl_3f, 0.99)
        var95_list.append(var95)
        var99_list.append(var99)
        
    plt.figure(figsize=(10, 6))
    plt.plot(twist_vols * 10000, np.array(var95_list) / 1e6, 'o-', color='orange', label='95% VaR')
    plt.plot(twist_vols * 10000, np.array(var99_list) / 1e6, 's-', color='red', label='99% VaR')
    plt.title("VaR Sensitivity to Twist Volatility", fontsize=14, fontweight='bold')
    plt.xlabel("Twist Volatility (basis points)")
    plt.ylabel("Value-at-Risk (INR Millions)")
    plt.legend(fontsize=11)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("mc_twist_sensitivity.png", dpi=300)
    plt.close()
    print("Twist sensitivity chart saved to: mc_twist_sensitivity.png")

def main():
    df = load_data()
    mc = BondRiskMC(df, n_sims=1000)
    
    # ----------------------------------------------------
    # Day 5: Parallel Shifts Only
    # ----------------------------------------------------
    shocks_p, pnl_dur, pnl_dc = mc.run_parallel_mc(vol_p=0.01)
    var95, cvar95 = calculate_var_cvar(pnl_dc, 0.95)
    var99, cvar99 = calculate_var_cvar(pnl_dc, 0.99)
    
    # Compare extreme scenarios (>150bps shift)
    print("=" * 60)
    print("DAY 5 DELIVERABLE: PARALLEL MONTE CARLO ANALYSIS")
    print("=" * 60)
    print("VaR/CVaR Statistics (Parallel Model):")
    print(f"  95% VaR:  INR {var95:,.2f}")
    print(f"  95% CVaR: INR {cvar95:,.2f}")
    print(f"  99% VaR:  INR {var99:,.2f}")
    print(f"  99% CVaR: INR {cvar99:,.2f}")
    print(f"  Max Gain: INR {pnl_dc.max():,.2f}")
    print(f"  Max Loss: INR {pnl_dc.min():,.2f}")
    print("-" * 60)
    
    # Find extreme scenarios (>150bps shift)
    extreme_idx = np.where(np.abs(shocks_p) > 0.015)[0]
    print(f"Number of extreme scenarios (>150bps): {len(extreme_idx)}")
    if len(extreme_idx) > 0:
        sample_idx = extreme_idx[:5]
        print("\nExtreme Scenarios Comparison:")
        for idx in sample_idx:
            shift_bps = shocks_p[idx] * 10000
            diff = pnl_dc[idx] - pnl_dur[idx]
            print(f"  Shift: {shift_bps:+.1f} bps | Duration P&L: INR {pnl_dur[idx]:+,.2f} | Dur+Conv P&L: INR {pnl_dc[idx]:+,.2f} | Convexity Bonus: INR {diff:+,.2f}")
            
    generate_day5_plots(shocks_p, pnl_dur, pnl_dc, var95, var99)
    print("Parallel MC charts saved successfully.")
    
    # ----------------------------------------------------
    # Day 6: 3-Factor Correlated Model
    # ----------------------------------------------------
    _, _, _, pnl_3f = mc.run_3factor_mc(vol_p=0.01, vol_t=0.005, vol_b=0.003)
    var95_3f, cvar95_3f = calculate_var_cvar(pnl_3f, 0.95)
    var99_3f, cvar99_3f = calculate_var_cvar(pnl_3f, 0.99)
    
    print("\n" + "=" * 60)
    print("DAY 6 DELIVERABLE: 3-FACTOR CORRELATED MONTE CARLO")
    print("=" * 60)
    print("VaR/CVaR Statistics (3-Factor Model):")
    print(f"  95% VaR:  INR {var95_3f:,.2f}")
    print(f"  95% CVaR: INR {cvar95_3f:,.2f}")
    print(f"  99% VaR:  INR {var99_3f:,.2f}")
    print(f"  99% CVaR: INR {cvar99_3f:,.2f}")
    print(f"  Max Gain: INR {pnl_3f.max():,.2f}")
    print(f"  Max Loss: INR {pnl_3f.min():,.2f}")
    
    # Save results to a CSV for later validation
    results_df = pd.DataFrame({
        "ScenarioID": range(1, 1001),
        "ParallelShift_bps": shocks_p * 10000,
        "PnL_DurationEffect_INR": pnl_dur,
        "PnL_ConvexityEffect_INR": pnl_dc - pnl_dur,
        "PnL_Total_INR": pnl_3f
    })
    results_df.to_csv("monte_carlo_results.csv", index=False)
    print("\nMonte Carlo scenario results exported to: monte_carlo_results.csv")
    
    # Compare VaRs
    var_comparison = {
        'parallel': np.array([var95, var99]),
        '3factor': np.array([var95_3f, var99_3f])
    }
    
    generate_day6_plots(pnl_3f, var95_3f, var99_3f, var_comparison)
    print("3-Factor MC charts saved successfully.")
    
    # Run twist sensitivity analysis
    run_sensitivity_analysis(mc)
    print("=" * 60)

if __name__ == "__main__":
    main()
