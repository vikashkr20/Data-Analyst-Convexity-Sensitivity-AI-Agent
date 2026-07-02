import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
from bond_pricing import bond_price

def load_data():
    try:
        df = pd.read_csv("bond_portfolio_recalc.csv")
    except FileNotFoundError:
        df = pd.read_csv("bond_portfolio_data.csv")
    return df

def calculate_krd_vector(face, coupon, ytm, years, freq, tenors):
    """
    Computes KRD vector of a bond for a list of tenors.
    Uses linear interpolation of yield curve shocks.
    """
    krd_vec = np.zeros(len(tenors))
    price_base = bond_price(face, coupon, ytm, years, freq)
    
    if price_base <= 0:
        return krd_vec
        
    bump_size = 0.0001 # 1 basis point (0.01%)
    
    # For each tenor point, we bump it by 1bp, interpolate the shock to the bond's maturity,
    # calculate the new price, and find the sensitivity.
    for j, T_j in enumerate(tenors):
        # Calculate the shock at the bond's maturity 'years' due to a bump at 'T_j'
        shock = 0.0
        
        if len(tenors) == 1:
            shock = 1.0
        else:
            if j == 0:
                if years <= T_j:
                    shock = 1.0
                elif years < tenors[1]:
                    shock = (tenors[1] - years) / (tenors[1] - T_j)
            elif j == len(tenors) - 1:
                if years >= T_j:
                    shock = 1.0
                elif years > tenors[j-1]:
                    shock = (years - tenors[j-1]) / (T_j - tenors[j-1])
            else:
                T_prev = tenors[j-1]
                T_next = tenors[j+1]
                if T_prev < years <= T_j:
                    shock = (years - T_prev) / (T_j - T_prev)
                elif T_j < years < T_next:
                    shock = (T_next - years) / (T_next - T_j)
                    
        # Apply the shocked YTM
        ytm_shocked = ytm + shock * bump_size
        price_shocked = bond_price(face, coupon, ytm_shocked, years, freq)
        
        # KRD = - (P_up - P_base) / (P_base * bump_size)
        krd_vec[j] = - (price_shocked - price_base) / (price_base * bump_size)
        
    return krd_vec

def run_krd_analysis():
    df = load_data()
    tenors = [0.25, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0]
    tenor_labels = ['3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
    
    # Calculate KRD vector for each bond
    bond_krds = []
    for idx, row in df.iterrows():
        face = row['FaceValue']
        coupon = row['CouponRate']
        ytm = row['YieldToMaturity']
        freq = row['CouponFrequency']
        years = math.floor(row['YearsToMaturity'] * freq) / freq
        if years <= 0:
            years = 0.25
            
        krd_vec = calculate_krd_vector(face, coupon, ytm, years, freq, tenors)
        bond_krds.append(krd_vec)
        
    krd_array = np.array(bond_krds) # Shape (301, 10)
    
    # Add KRD columns to DataFrame
    for j, label in enumerate(tenor_labels):
        df[f'KRD_{label}'] = krd_array[:, j]
        
    # Portfolio aggregated KRD vector (weighted sum using PortfolioWeight)
    weights = df['PortfolioWeight'].values
    portfolio_krd = np.dot(weights, krd_array)
    
    # Calculate portfolio Modified Duration (weighted sum of ModifiedDuration)
    # Let's use the ModDur column in the dataframe
    if 'Recalc_ModifiedDuration' in df.columns:
        port_mod_dur = (df['Recalc_ModifiedDuration'] * df['PortfolioWeight']).sum()
    else:
        port_mod_dur = (df['ModifiedDuration'] * df['PortfolioWeight']).sum()
        
    sum_krds = np.sum(portfolio_krd)
    
    print("=" * 60)
    print("DAY 4 DELIVERABLE: KEY RATE DURATION (KRD) ANALYSIS")
    print("=" * 60)
    print("Portfolio KRD Vector:")
    for label, val in zip(tenor_labels, portfolio_krd):
        print(f"  KRD {label:3s}: {val:.4f}")
    print("-" * 60)
    print(f"Sum of Portfolio KRDs:       {sum_krds:.4f} Years")
    print(f"Portfolio Modified Duration: {port_mod_dur:.4f} Years")
    print(f"Discrepancy (Sum vs ModDur): {abs(sum_krds - port_mod_dur):.6f} ({abs(sum_krds - port_mod_dur)/port_mod_dur*100:.4f}%)")
    print("=" * 60)
    
    # Check if portfolio is bullet, barbell, or ladder
    # Let's inspect which tenors have the highest weights
    # If short and long are high, it's barbell. If belly is high, it's bullet.
    short_end = portfolio_krd[0:4].sum() # 3M to 2Y
    belly = portfolio_krd[4:7].sum()     # 3Y to 7Y
    long_end = portfolio_krd[7:10].sum()  # 10Y to 30Y
    print("\nPortfolio Shape Analysis:")
    print(f"  Short-end (3M-2Y) KRD contribution: {short_end:.4f} ({short_end/sum_krds*100:.2f}%)")
    print(f"  Belly (3Y-7Y) KRD contribution:     {belly:.4f} ({belly/sum_krds*100:.2f}%)")
    print(f"  Long-end (10Y-30Y) KRD contribution: {long_end:.4f} ({long_end/sum_krds*100:.2f}%)")
    
    # Save the updated data with KRDs
    df.to_csv("bond_portfolio_krd.csv", index=False)
    print("\nUpdated portfolio data with individual KRD vectors saved to: bond_portfolio_krd.csv")
    
    # Build KRD Heatmap by CreditRating × Tenor
    # Weighted average KRD for each rating
    rating_krd = []
    ratings = df['CreditRating'].unique()
    for rating in ratings:
        rating_df = df[df['CreditRating'] == rating]
        rating_weight = rating_df['PortfolioWeight'].sum()
        if rating_weight > 0:
            rating_krd_vec = np.dot(rating_df['PortfolioWeight'].values / rating_weight, krd_array[rating_df.index, :])
            rating_krd.append(rating_krd_vec)
        else:
            rating_krd.append(np.zeros(len(tenors)))
            
    rating_krd_df = pd.DataFrame(rating_krd, index=ratings, columns=tenor_labels)
    
    plt.figure(figsize=(12, 6))
    sns.heatmap(rating_krd_df, annot=True, fmt=".4f", cmap="YlOrRd", cbar_kws={'label': 'Weighted KRD'})
    plt.title("Key Rate Duration Heatmap (Credit Rating × Tenor)", fontsize=14, fontweight='bold')
    plt.xlabel("Tenor Bucket")
    plt.ylabel("Credit Rating")
    plt.tight_layout()
    plt.savefig("krd_heatmap.png", dpi=300)
    plt.close()
    print("KRD Heatmap saved to: krd_heatmap.png")
    
    # Scenario testing: steepening shock
    # Short up 50bps, long up 25bps.
    # Let's interpolate this shock to the tenors:
    # 3M to 2Y (short) get +50bps. 10Y to 30Y (long) get +25bps.
    # What about the intermediate belly? Linear interpolation between 2Y (+50bps) and 10Y (+25bps).
    shocks_bps = np.zeros(len(tenors))
    for j, t in enumerate(tenors):
        if t <= 2.0:
            shocks_bps[j] = 50.0
        elif t >= 10.0:
            shocks_bps[j] = 25.0
        else:
            # Linear interpolation between 2Y (+50bps) and 10Y (+25bps)
            shocks_bps[j] = 50.0 + (t - 2.0) / (10.0 - 2.0) * (25.0 - 50.0)
            
    shocks_dec = shocks_bps / 10000 # convert to decimals
    print("\n" + "=" * 60)
    print("SCENARIO TESTING: STEEPENING SHOCK (Short +50bps, Long +25bps)")
    print("=" * 60)
    print("Tenor Shocks (bps):")
    for label, shock in zip(tenor_labels, shocks_bps):
        print(f"  {label:3s}: {shock:.1f} bps")
        
    total_mv = df['MarketValue_INR'].sum()
    
    # Compute P&L using KRD vector
    # P&L_j = - KRD_j * shock_j * MV
    pnl_by_tenor = - portfolio_krd * shocks_dec * total_mv
    total_pnl = np.sum(pnl_by_tenor)
    
    print("-" * 60)
    print("P&L Impact by Tenor (INR):")
    for label, pnl_t in zip(tenor_labels, pnl_by_tenor):
        print(f"  {label:3s}: INR {pnl_t:,.2f}")
    print("-" * 60)
    print(f"Total Portfolio KRD P&L Impact: INR {total_pnl:,.2f}")
    print("=" * 60)

if __name__ == "__main__":
    run_krd_analysis()
