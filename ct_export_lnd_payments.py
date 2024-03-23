#!/usr/bin/env python3
import json

import pandas as pd

BTC = "BTC"
LN = "LBTC2"
EXCHANGE = "raspiblitz"

pd.options.display.float_format = '{:.8f}'.format

# take the output from `lncli listpayments` as input
with open("payments.json", "r") as f:
    s = f.read()

data = json.loads(s)

df = pd.json_normalize(data, 'payments')
df = df.astype({'value': 'float64', 'value_sat': 'float64', 'value_msat': 'float64',
                'fee_sat': 'int64', 'creation_date': 'int64'})
df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s', utc=False)

# only care for outgoing payments that were successful and worth 1000 satoshis or more
filtered_df = df.query('status == "SUCCEEDED" and value_sat >= 1000')
# filtered_df.to_excel('payments.xlsx', index=False)  # Excel needs "utc=False" on dates

# new dataframe for CoinTracking
ct_df = pd.DataFrame(
    columns=['Type',
             'Buy Amount', 'Buy Currency',
             'Sell Amount', 'Sell Currency',
             'Fee', 'Fee Currency',
             'Exchange', 'Trade-Group',
             'Comment',
             'Date',
             'Tx-ID'])

for i, row in filtered_df.iterrows():
    ct_df.loc[i] = {
        'Type': 'Withdrawal',
        'Sell Amount': row['value_sat'] / 100000000.0, 'Sell Currency': LN,
        'Fee': row['fee_sat'] / 100000000.0, 'Fee Currency': LN,
        'Exchange': EXCHANGE, 'Trade-Group': 'LN-Payments',
        'Date': row['creation_date'],
        'Tx-ID': f"ln_out: {row['payment_hash']}"
    }

print(ct_df.info())
# print(ct_df)
ct_df.to_csv('ct_out_payments.csv', index=False, date_format='%s', float_format='%.8f')
