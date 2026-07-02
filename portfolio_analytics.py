import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def load_data():
    # Load recalculated data if available, otherwise original
    try:
        df = pd.read_csv("bond_portfolio_recalc.csv")
        # Use recalculated columns
        df['ModDur'] = df['Recalc_ModifiedDuration']
        df['Conv'] = df['Recalc_Convexity']
        df['DV01'] = df['Recalc_DV01']
    except FileNotFoundError:
        df = pd.read_csv("bond_portfolio_data.csv")
        df['ModDur'] = df['ModifiedDuration']
        df['Conv'] = df['Convexity']
        df['DV01'] = df['DV01_Per100Face'] * df['Quantity'] / 100
        
    return df

def run_portfolio_analytics():
    df = load_data()
    
    # Calculate portfolio market value in INR
    total_mv = df['MarketValue_INR'].sum()
    print(f"Total Portfolio Market Value: INR {total_mv:,.2f}")
    
    # Portfolio level aggregates
    # 1. MV-weighted Modified Duration
    port_mod_dur = (df['ModDur'] * df['PortfolioWeight']).sum()
    
    # 2. MV-weighted Convexity
    port_conv = (df['Conv'] * df['PortfolioWeight']).sum()
    
    # 3. Total portfolio DV01 (sum of individual DV01 * quantity / 100)
    # The DV01_Per100Face is per 100 face value. Total DV01 = sum(DV01_Per100Face * Quantity / 100)
    # In our recalc we stored absolute DV01 for each bond as Recalc_DV01.
    # Let's compute it.
    total_dv01 = (df['DV01_Per100Face'] * df['Quantity'] / 100).sum()
    
    print("\n" + "=" * 60)
    print("PORTFOLIO LEVEL RISK AGGREGATES")
    print("=" * 60)
    print(f"Portfolio Modified Duration: {port_mod_dur:.4f} Years")
    print(f"Portfolio Convexity:         {port_conv:.4f}")
    print(f"Portfolio Total DV01 (INR):  {total_dv01:,.2f}")
    print("=" * 60)
    
    # Contributions
    # Duration Contribution = SUM(ModifiedDuration_i * PortfolioWeight_i)
    # 1. Credit Rating
    rating_contrib = df.groupby('CreditRating').apply(lambda x: (x['ModDur'] * x['PortfolioWeight']).sum()).reset_index(name='Contribution')
    rating_contrib['Pct_Contribution'] = rating_contrib['Contribution'] / port_mod_dur
    print("\nDuration Contribution by Credit Rating:")
    print(rating_contrib.to_string(index=False))
    
    # 2. Sector
    sector_contrib = df.groupby('Sector').apply(lambda x: (x['ModDur'] * x['PortfolioWeight']).sum()).reset_index(name='Contribution')
    sector_contrib['Pct_Contribution'] = sector_contrib['Contribution'] / port_mod_dur
    print("\nDuration Contribution by Sector:")
    print(sector_contrib.to_string(index=False))
    
    # 3. Currency
    currency_contrib = df.groupby('Currency').apply(lambda x: (x['ModDur'] * x['PortfolioWeight']).sum()).reset_index(name='Contribution')
    currency_contrib['Pct_Contribution'] = currency_contrib['Contribution'] / port_mod_dur
    print("\nDuration Contribution by Currency:")
    print(currency_contrib.to_string(index=False))
    
    # 4. Key Rate Bucket
    krd_contrib = df.groupby('KeyRateBucket').apply(lambda x: (x['ModDur'] * x['PortfolioWeight']).sum()).reset_index(name='Contribution')
    krd_contrib['Pct_Contribution'] = krd_contrib['Contribution'] / port_mod_dur
    # Sort KRD buckets logically
    bucket_order = {'0-1Y': 0, '1-2Y': 1, '2-3Y': 2, '3-5Y': 3, '5-7Y': 4, '7-10Y': 5, '10-15Y': 6, '15-20Y': 7, '20Y+': 8}
    krd_contrib['Order'] = krd_contrib['KeyRateBucket'].map(bucket_order)
    krd_contrib = krd_contrib.sort_values('Order').drop(columns=['Order'])
    print("\nDuration Contribution by Key Rate Bucket (CSV Categories):")
    print(krd_contrib.to_string(index=False))
    
    # Total DV01 by Currency
    currency_dv01 = df.groupby('Currency').apply(lambda x: (x['DV01_Per100Face'] * x['Quantity'] / 100).sum()).reset_index(name='DV01')
    print("\nDV01 by Currency (INR):")
    print(currency_dv01.to_string(index=False))
    
    # Plotting
    sns.set_theme(style="darkgrid")
    
    # Chart 1: Duration Contribution by Rating (Pie Chart)
    plt.figure(figsize=(8, 6))
    plt.pie(rating_contrib['Contribution'], labels=rating_contrib['CreditRating'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette("viridis", len(rating_contrib)))
    plt.title("Duration Contribution by Credit Rating", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("duration_contribution_rating.png", dpi=300)
    plt.close()
    
    # Chart 2: Key Rate Duration Contribution (Bar Chart)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=krd_contrib, x='KeyRateBucket', y='Contribution', palette='magma')
    plt.title("Key Rate Duration Contribution (CSV Buckets)", fontsize=14, fontweight='bold')
    plt.xlabel("Maturity Bucket")
    plt.ylabel("Contribution to Portfolio Duration")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("krd_contribution.png", dpi=300)
    plt.close()
    
    # Chart 3: DV01 by Currency (Column Chart)
    plt.figure(figsize=(8, 6))
    sns.barplot(data=currency_dv01, x='Currency', y='DV01', palette='rocket')
    plt.title("DV01 by Currency (INR)", fontsize=14, fontweight='bold')
    plt.xlabel("Currency")
    plt.ylabel("DV01 (INR)")
    plt.tight_layout()
    plt.savefig("dv01_by_currency.png", dpi=300)
    plt.close()
    
    # Chart 4: Portfolio P&L Sensitivity Curve
    yield_shifts_bps = np.linspace(-200, 200, 100)
    pnl_dur_only = []
    pnl_dur_conv = []
    
    for shift in yield_shifts_bps:
        dy = shift / 10000 # convert bps to decimal
        pnl_d = -port_mod_dur * dy * total_mv
        pnl_c = pnl_d + 0.5 * port_conv * (dy**2) * total_mv
        pnl_dur_only.append(pnl_d)
        pnl_dur_conv.append(pnl_c)
        
    plt.figure(figsize=(10, 6))
    plt.plot(yield_shifts_bps, np.array(pnl_dur_only) / 1e7, 'r--', label='Duration Only (Linear)')
    plt.plot(yield_shifts_bps, np.array(pnl_dur_conv) / 1e7, 'b-', label='Duration + Convexity (Quadratic)')
    plt.axhline(0, color='black', linewidth=0.8, linestyle=':')
    plt.axvline(0, color='black', linewidth=0.8, linestyle=':')
    plt.title("Portfolio P&L Sensitivity to Interest Rate Shifts", fontsize=14, fontweight='bold')
    plt.xlabel("Yield Curve Shift (basis points)")
    plt.ylabel("Portfolio P&L (INR Crores)")
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig("portfolio_pnl_sensitivity.png", dpi=300)
    plt.close()
    
    print("\nFour charts saved successfully:")
    print("  1. duration_contribution_rating.png")
    print("  2. krd_contribution.png")
    print("  3. dv01_by_currency.png")
    print("  4. portfolio_pnl_sensitivity.png")
    
    # Scenario testing: parallel shock of +100bps
    dy_100 = 0.01
    pnl_100_dur = -port_mod_dur * dy_100 * total_mv
    pnl_100_conv = 0.5 * port_conv * (dy_100**2) * total_mv
    pnl_100_total = pnl_100_dur + pnl_100_conv
    print("\n" + "=" * 60)
    print("SCENARIO TESTING: +100bps PARALLEL SHIFT")
    print("=" * 60)
    print(f"Duration Effect:  INR {pnl_100_dur:,.2f}")
    print(f"Convexity Effect: INR {pnl_100_conv:,.2f}")
    print(f"Total P&L Impact: INR {pnl_100_total:,.2f}")
    print(f"Convexity saved:  INR {pnl_100_conv:,.2f} ({pnl_100_conv / abs(pnl_100_dur) * 100:.2f}% of duration losses)")
    print("=" * 60)

if __name__ == "__main__":
    run_portfolio_analytics()
