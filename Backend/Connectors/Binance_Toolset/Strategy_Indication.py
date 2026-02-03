import pandas as pd

def label_day(row):
    """Label single day as LONG / SHORT / NEUTRAL"""
    if row['Close'] > row['Open']:
        return "LONG"
    elif row['Close'] < row['Open']:
        return "SHORT"
    else:
        return "NEUTRAL"


def volume_strength(row):
    """Simple volume confirmation score"""
    price_change = row['Close'] - row['Open']
    vol = row['Volume']

    if price_change > 0 and vol > row['Volume_avg']:
        return 1.0   # strong bullish confirmation
    elif price_change < 0 and vol > row['Volume_avg']:
        return -1.0  # strong bearish confirmation
    elif price_change > 0:
        return 0.5
    elif price_change < 0:
        return -0.5
    else:
        return 0.0


def taker_pressure(row):
    """Taker buy pressure signal"""
    if row['Taker Buy Base Volume'] > row['Taker_avg']:
        if row['Close'] > row['Open']:
            return 1.0
        else:
            return -0.5
    return 0.0


def final_conclusion(df, last_days_analysis: int = 7):
    recent = df.iloc[-last_days_analysis:]

    long_days = (recent['label'] == "LONG").sum()
    short_days = (recent['label'] == "SHORT").sum()

    avg_score = recent['daily_score'].mean()
    avg_vs_btc = recent['vs_btc'].mean()

    # Trend bias
    if long_days > short_days:
        trend = "bullish (lean LONG)"
    elif short_days > long_days:
        trend = "bearish (lean SHORT)"
    else:
        trend = "mixed / unclear"

    # Volume & taker confidence
    if avg_score > 0.6:
        strength = "strong momentum"
    elif avg_score > 0:
        strength = "moderate momentum"
    elif avg_score > -0.6:
        strength = "weak momentum"
    else:
        strength = "strong counter-momentum"

    # BTC comparison
    if avg_vs_btc > 0.5:
        relative = "outperforming BTC"
    elif avg_vs_btc < -0.5:
        relative = "underperforming BTC"
    else:
        relative = "moving roughly with BTC"

    conclusion = f"""
Over the last {last_days_analysis} days:

- Trend: {trend}
- Long days: {long_days} | Short days: {short_days}
- Momentum strength: {strength}
- Market comparison: {relative}

Final stance: 
"""

    if long_days > short_days and avg_vs_btc > 0:
        conclusion += "PROBABLE LONG BIAS"
    elif short_days > long_days and avg_vs_btc < 0:
        conclusion += "PROBABLE SHORT BIAS"
    else:
        conclusion += "NO CLEAR EDGE — wait for confirmation"

    return conclusion

def prepare_df(df, average_rolling: int = 5):
    df = df.copy()

    # daily % change
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    df['Taker Buy Base Volume'] = pd.to_numeric(df['Taker Buy Base Volume'], errors='coerce')
    df['pct_change'] = df['Close'].pct_change()*100

    # rolling volume average (5 days)
    df['Volume_avg'] = df['Volume'].rolling(average_rolling).mean()

    # rolling taker average
    df['Taker_avg'] = df['Taker Buy Base Volume'].rolling(average_rolling).mean()

    # label each day
    df['label'] = df.apply(label_day, axis=1)

    # signal strength components
    df['vol_signal'] = df.apply(volume_strength, axis=1)
    df['taker_signal'] = df.apply(taker_pressure, axis=1)

    # combined daily score
    df['daily_score'] = df['vol_signal'] + df['taker_signal']

    return df

def produce_conclusion(df, df_btc, average_rolling: int = 5,days_to_analyze: int = 7):
    df = prepare_df(df, average_rolling=average_rolling)
    df_btc = prepare_df(df_btc, average_rolling=average_rolling)

    common = df.index.intersection(df_btc.index)

    df = df.loc[common]
    df_btc = df_btc.loc[common]

    df['vs_btc'] = df['pct_change'] - df_btc['pct_change']

    return final_conclusion(df, last_days_analysis=days_to_analyze)
