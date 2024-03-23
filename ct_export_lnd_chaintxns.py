#!/usr/bin/env python3
import json

import pandas as pd

BTC = "BTC"
LN = "LBTC2"
EXCHANGE = "raspiblitz"

pd.options.display.float_format = '{:.8f}'.format

# take the output from `lncli listchaintxns` as input
with open("chaintxns.json", "r") as f:
    s = f.read()

data = json.loads(s)

df = pd.json_normalize(data, 'transactions')
df = df.astype({'amount': 'float64', 'total_fees': 'float64', 'time_stamp': 'int64'})
df['time_stamp'] = pd.to_datetime(df['time_stamp'], unit='s', utc=True)

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

for i, row in df.iterrows():
    if row['amount'] >= 0:
        ct_df.loc[i] = {
            'Type': 'Deposit',
            'Buy Amount': row['amount'] / 100000000.0, 'Buy Currency': BTC,
            'Fee': row['total_fees'] / 100000000.0, 'Fee Currency': BTC,
            'Exchange': EXCHANGE, 'Trade-Group': 'LN-Chaintxns',
            'Comment': row['label'],
            'Date': row['time_stamp'],
            'Tx-ID': f"chain_in: {row['tx_hash']}"
        }

    else:
        ct_df.loc[i] = {
            'Type': 'Withdrawal',
            'Sell Amount': row['amount'] * -1 / 100000000.0, 'Sell Currency': BTC,
            'Fee': row['total_fees'] / 100000000.0, 'Fee Currency': BTC,
            'Exchange': EXCHANGE, 'Trade-Group': 'LN-Chaintxns',
            'Comment': row['label'],
            'Date': row['time_stamp'],
            'Tx-ID': f"chain_out: {row['tx_hash']}"
        }

# print(ct_df.info())
# print(ct_df)
ct_df.to_csv('ct_out_chaintxns.csv', index=False, date_format='%s', float_format='%.8f')
