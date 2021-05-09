import pyupbit
import numpy as np


def get_ror(k=0.5):
    df = pyupbit.get_ohlcv("KRW-XRP",count=4)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)

    fee = 0
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

bestK = 0.0
ror2 = 0.0
for k in np.arange(0.1, 1.0, 0.1):

    ror = get_ror(k)
    if ror2 < ror:
        ror2 = ror
        bestK = k
    print("%.1f %f" % (k, ror))
if ror2 < 1.01:
    bestK = 0
print("ff:", ror2, bestK)