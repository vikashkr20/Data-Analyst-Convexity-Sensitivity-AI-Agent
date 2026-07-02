import pandas as pd
import numpy as np
import math

def bond_price(face, coupon_rate, ytm, years, freq=2):
    """
    Calculates the dirty price of a bond from first principles.
    Supports both coupon bonds and zero-coupon bonds.
    """
    if years <= 0:
        return face
    
    # If it is a zero-coupon bond (like a T-Bill)
    if coupon_rate == 0:
        return face / ((1 + ytm / freq) ** (years * freq))
        
    c = face * coupon_rate / freq
    n = int(years * freq)
    r = ytm / freq
    
    price = 0
    for t in range(1, n + 1):
        cf = c if t < n else c + face
        price += cf / ((1 + r) ** t)
    return price

def macaulay_duration(face, coupon_rate, ytm, years, freq=2):
    """
    Calculates the Macaulay duration in years from first principles.
    """
    if years <= 0:
        return 0.0
    
    if coupon_rate == 0:
        return years
        
    c = face * coupon_rate / freq
    n = int(years * freq)
    r = ytm / freq
    price = bond_price(face, coupon_rate, ytm, years, freq)
    
    mac_dur = 0
    for t in range(1, n + 1):
        cf = c if t < n else c + face
        pv = cf / ((1 + r) ** t)
        mac_dur += (t / freq) * pv
    return mac_dur / price

def modified_duration(face, coupon_rate, ytm, years, freq=2):
    """
    Calculates the Modified duration in years from first principles.
    """
    if years <= 0:
        return 0.0
    
    mac_dur = macaulay_duration(face, coupon_rate, ytm, years, freq)
    r = ytm / freq
    return mac_dur / (1 + r)

def convexity(face, coupon_rate, ytm, years, freq=2):
    """
    Calculates the convexity of a bond in annual terms from first principles.
    """
    if years <= 0:
        return 0.0
        
    c = face * coupon_rate / freq
    n = int(years * freq)
    r = ytm / freq
    price = bond_price(face, coupon_rate, ytm, years, freq)
    
    conv = 0
    for t in range(1, n + 1):
        cf = c if t < n else c + face
        pv = cf / ((1 + r) ** t)
        conv += t * (t + 1) * pv
    return conv / (price * freq**2 * (1 + r)**2)

def dv01(face, coupon_rate, ytm, years, freq=2):
    """
    Calculates the DV01 (Price Value of a Basis Point) per 100 face value.
    """
    mod_dur = modified_duration(face, coupon_rate, ytm, years, freq)
    price = bond_price(face, coupon_rate, ytm, years, freq)
    return mod_dur * price / 10000

def validate_test_bonds():
    print("=" * 60)
    print("DAY 2 DELIVERABLE: TEST BOND VALIDATION")
    print("=" * 60)
    
    # Test Bond 1: 7.26% GOI 2033 (YTM 7.35%, 9.0 years, freq 2)
    b1_price = bond_price(100, 0.0726, 0.0735, 9.0, 2)
    b1_mac = macaulay_duration(100, 0.0726, 0.0735, 9.0, 2)
    b1_mod = modified_duration(100, 0.0726, 0.0735, 9.0, 2)
    b1_conv = convexity(100, 0.0726, 0.0735, 9.0, 2)
    b1_dv01 = dv01(100, 0.0726, 0.0735, 9.0, 2)
    
    print("Test Bond 1: 7.26% GOI 2033 (YTM 7.35%, 9.0Y)")
    print(f"  Calculated Price: {b1_price:.6f} | Excel PRICE(): 99.414983 (Diff: {b1_price - 99.414983:.6f})")
    print(f"  Calculated MacDur: {b1_mac:.6f} | Excel DURATION(): 6.753609 (Diff: {b1_mac - 6.753609:.6f})")
    print(f"  Calculated ModDur: {b1_mod:.6f} | Excel MDURATION(): 6.514212 (Diff: {b1_mod - 6.514212:.6f})")
    print(f"  Calculated Convexity: {b1_conv:.6f} (Annualized)")
    print(f"  Calculated DV01: {b1_dv01:.6f} per 100 Face")
    
    # Test Bond 2: 91-day T-Bill (YTM 6.5%, 91/365 = 0.2493 years, freq 2)
    # T-Bills are zero coupon bonds (coupon = 0)
    # Excel PRICE is 100 - YTM * 91/360 * 100 (for T-Bills in US) or standard discount
    # Let's check with standard zero-coupon formula:
    years_tb = 91 / 365.25
    b2_price = bond_price(100, 0.0, 0.065, years_tb, 2)
    b2_mac = macaulay_duration(100, 0.0, 0.065, years_tb, 2)
    b2_mod = modified_duration(100, 0.0, 0.065, years_tb, 2)
    b2_conv = convexity(100, 0.0, 0.065, years_tb, 2)
    b2_dv01 = dv01(100, 0.0, 0.065, years_tb, 2)
    
    print("\nTest Bond 2: 91-day T-Bill (YTM 6.5%, 91 days)")
    print(f"  Calculated Price: {b2_price:.6f}")
    print(f"  Calculated MacDur: {b2_mac:.6f} (Theoretical: {years_tb:.6f})")
    print(f"  Calculated ModDur: {b2_mod:.6f}")
    print(f"  Calculated Convexity: {b2_conv:.6f}")
    print(f"  Calculated DV01: {b2_dv01:.6f}")
    
    # Test Bond 3: 8.5% AAA Corp 2027 (YTM 8.2%, 3.0 years, freq 2)
    b3_price = bond_price(100, 0.085, 0.082, 3.0, 2)
    b3_mac = macaulay_duration(100, 0.085, 0.082, 3.0, 2)
    b3_mod = modified_duration(100, 0.085, 0.082, 3.0, 2)
    b3_conv = convexity(100, 0.085, 0.082, 3.0, 2)
    b3_dv01 = dv01(100, 0.085, 0.082, 3.0, 2)
    
    print("\nTest Bond 3: 8.5% AAA Corp 2027 (YTM 8.2%, 3.0Y)")
    print(f"  Calculated Price: {b3_price:.6f} | Excel PRICE(): 100.779774 (Diff: {b3_price - 100.779774:.6f})")
    print(f"  Calculated MacDur: {b3_mac:.6f} | Excel DURATION(): 2.695383 (Diff: {b3_mac - 2.695383:.6f})")
    print(f"  Calculated ModDur: {b3_mod:.6f} | Excel MDURATION(): 2.589225 (Diff: {b3_mod - 2.589225:.6f})")
    print(f"  Calculated Convexity: {b3_conv:.6f}")
    print(f"  Calculated DV01: {b3_dv01:.6f}")
    print("=" * 60)

def process_portfolio():
    print("PROCESSING PORTFOLIO DATA...")
    portfolio_path = "bond_portfolio_data.csv"
    df = pd.read_csv(portfolio_path)
    
    recalc_prices = []
    recalc_mac_dur = []
    recalc_mod_dur = []
    recalc_conv = []
    recalc_dv01 = []
    
    for idx, row in df.iterrows():
        face = row['FaceValue']
        coupon = row['CouponRate']
        ytm = row['YieldToMaturity']
        freq = row['CouponFrequency']
        
        # Rounded years to match the dataset's rounding convention
        years = math.floor(row['YearsToMaturity'] * freq) / freq
        if years <= 0:
            years = 0.25
            
        # Re-calculate
        price = bond_price(face, coupon, ytm, years, freq)
        mac = macaulay_duration(face, coupon, ytm, years, freq)
        mod = modified_duration(face, coupon, ytm, years, freq)
        
        # Convexity without freq**2 in denominator for the CSV form,
        # but let's calculate standard convexity and period convexity
        c = face * coupon / freq
        n = int(years * freq)
        r = ytm / freq
        conv_sum = sum(t * (t + 1) * (cf / ((1 + r) ** t)) for t in range(1, n + 1) for cf in [c if t < n else c + face])
        conv_val_csv_form = conv_sum / (price * (1 + r)**2)
        
        dv01_val = mod * price / 10000
        
        recalc_prices.append(price)
        recalc_mac_dur.append(mac)
        recalc_mod_dur.append(mod)
        recalc_conv.append(conv_val_csv_form)
        recalc_dv01.append(dv01_val)
        
    df['Recalc_CleanPrice'] = recalc_prices
    df['Recalc_MacaulayDuration'] = recalc_mac_dur
    df['Recalc_ModifiedDuration'] = recalc_mod_dur
    df['Recalc_Convexity'] = recalc_conv
    df['Recalc_DV01'] = recalc_dv01
    
    # Save the recalculated values to a new file for downstream tasks
    output_path = "bond_portfolio_recalc.csv"
    df.to_csv(output_path, index=False)
    print(f"Recalculated portfolio saved to: {output_path}")
    
    # Generate Summary Statistics
    print("\n" + "=" * 60)
    print("PORTFOLIO SUMMARY STATISTICS BY CREDIT RATING")
    print("=" * 60)
    rating_stats = df.groupby('CreditRating')[['Recalc_ModifiedDuration', 'Recalc_Convexity', 'Recalc_DV01']].agg(['min', 'max', 'mean', 'median'])
    print(rating_stats.to_string())
    
    print("\n" + "=" * 60)
    print("PORTFOLIO SUMMARY STATISTICS BY SECTOR")
    print("=" * 60)
    sector_stats = df.groupby('Sector')[['Recalc_ModifiedDuration', 'Recalc_Convexity', 'Recalc_DV01']].agg(['min', 'max', 'mean', 'median'])
    print(sector_stats.to_string())
    
if __name__ == "__main__":
    validate_test_bonds()
    process_portfolio()
