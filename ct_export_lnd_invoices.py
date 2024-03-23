#!/usr/bin/env python3
import json

import pandas as pd

BTC = "BTC"
LN = "LBTC2"
EXCHANGE = "raspiblitz"

pd.options.display.float_format = '{:.8f}'.format

# take the output from `lncli listinvoices` as input
with open("invoices.json", "r") as f:
    s = f.read()

data = json.loads(s)

df = pd.json_normalize(data, 'invoices')
df = df.astype({'value': 'float64', 'value_msat': 'float64',
                'amt_paid': 'float64', 'amt_paid_sat': 'float64', 'amt_paid_msat': 'float64',
                'add_index': 'int64', 'settle_index': 'int64',
                'settle_date': 'int64', 'creation_date': 'int64'})
df['creation_date'] = pd.to_datetime(df['creation_date'], unit='s', utc=True)
df['settle_date'] = pd.to_datetime(df['settle_date'], unit='s', utc=True)

# only care for settled invoices (incoming payments) that were worth 1000 satoshis or more
filtered_df = df.query('state == "SETTLED" and amt_paid_sat >= 1000')
# filtered_df.to_excel('invoices.xlsx', index=False)  # Excel needs "utc=False" on dates

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
        'Type': 'Deposit',
        'Buy Amount': row['amt_paid_sat'] / 100000000.0, 'Buy Currency': LN,
        'Exchange': EXCHANGE, 'Trade-Group': 'LN-Invoices',
        'Comment': row['memo'],
        'Date': row['settle_date'],
        'Tx-ID': f"ln_in: {row['r_hash']}"
    }

print(ct_df.info())
# print(ct_df)
ct_df.to_csv('ct_out_invoices.csv', index=False, date_format='%s', float_format='%.8f')
