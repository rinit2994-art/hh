#!/usr/bin/env python3
"""Test the notebook with real mutual fund data"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import all necessary libraries first
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

from scipy import stats
from scipy.optimize import minimize
from datetime import datetime, timedelta

import xgboost as xgb
import lightgbm as lgb

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('seaborn-v0_8-darkgrid')

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.float_format', '{:.3f}'.format)

# Load the notebook to get all function definitions
import nbformat
from nbconvert import PythonExporter

print("Loading notebook functions...")
with open('mutual_fund_profit_predictor.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

# Extract only code cells
exporter = PythonExporter()
code, _ = exporter.from_notebook_node(nb)

# Execute the code to define functions
exec(code, globals())

print("\n" + "="*80)
print("TESTING WITH REAL MUTUAL FUND DATA")
print("="*80)

df = pd.read_csv('real_mutual_funds.csv')
print(f"\nLoaded {len(df)} real mutual funds with {len(df.columns)} features")

print("\nColumn names:")
print(df.columns.tolist())

print("\nSample data:")
print(df.head(2))

print("\n" + "="*80)
print("RUNNING PROFIT MAXIMIZATION ANALYSIS")
print("="*80)

results_df, recommendations = maximize_profits(df)

print("\n" + "="*80)
print("✅ TEST COMPLETED SUCCESSFULLY!")
print("="*80)
print(f"\nResults shape: {results_df.shape}")
print(f"Recommendations for {len(recommendations)} risk profiles")

if 'QUANTUM_SCORE' in results_df.columns:
    print(f"\nQuantum Score range: {results_df['QUANTUM_SCORE'].min():.1f} - {results_df['QUANTUM_SCORE'].max():.1f}")

if 'MASTER_PREDICTION' in results_df.columns:
    print(f"Predicted returns range: {results_df['MASTER_PREDICTION'].min():.1f}% - {results_df['MASTER_PREDICTION'].max():.1f}%")

print("\nTop 3 funds by Quantum Score:")
top_funds = results_df.nlargest(3, 'QUANTUM_SCORE')[['Name', 'QUANTUM_SCORE', 'Sharpe Ratio', 'Expense Ratio']]
print(top_funds.to_string())

print("\n✅ All tests passed with real data!")
