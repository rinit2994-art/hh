"""
Agentic Mutual Fund Profit Maximizer using Google ADK

A multi-agent system that autonomously analyzes mutual funds, makes predictions,
and provides optimized portfolio recommendations.

Architecture:
- OrchestratorAgent: Coordinates the entire analysis workflow
- DataAgent: Handles data loading, validation, and preprocessing
- FeatureAgent: Performs feature engineering and quantum scoring
- MLAgent: Builds ML models and generates predictions
- PortfolioAgent: Optimizes portfolios and creates recommendations
- ReportAgent: Generates visualizations and reports
"""

import os
import pandas as pd
import numpy as np
import warnings
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
warnings.filterwarnings('ignore')

# Machine Learning
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False

# Google ADK imports
try:
    from adk.agents import Agent, tool
    from adk.runners import DirectRunner
    from adk.models import Model
    ADK_AVAILABLE = True
except ImportError:
    print("⚠️ Google ADK not available. Installing...")
    ADK_AVAILABLE = False


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AnalysisResult:
    """Container for analysis results"""
    df: pd.DataFrame
    predictions: Dict[str, Any]
    recommendations: Dict[str, pd.DataFrame]
    regime: str
    regime_score: int
    strategy: str


# ============================================================================
# TOOL FUNCTIONS (Pure Python functions that agents can use)
# ============================================================================

def load_and_validate_data(csv_path: str) -> pd.DataFrame:
    """Load and validate mutual fund data"""
    print(f"📂 Loading data from {csv_path}...")

    if isinstance(csv_path, str):
        df = pd.read_csv(csv_path)
    else:
        df = csv_path

    print(f"✅ Loaded {len(df)} funds with {len(df.columns)} features")

    # Convert numeric columns
    numeric_cols = [col for col in df.columns if col not in ['Name', 'Sub Category', 'Plan', 'AMC',
                                                              'Benchmark', 'Exit Load', 'Fund Manager',
                                                              'SIP Investment', 'SEBI Risk Category']]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Remove duplicate plans
    initial_len = len(df)
    df = df[~df['Name'].str.contains('IDCW|Dividend|Direct', case=False, na=False)]
    print(f"  • Removed {initial_len - len(df)} duplicate plans")
    print(f"  • Analyzing {len(df)} unique funds")

    return df


def engineer_quantum_features(df: pd.DataFrame) -> pd.DataFrame:
    """Creates advanced predictive features using financial engineering"""
    print("\n🔬 ENGINEERING QUANTUM PREDICTIVE FEATURES...")

    df = df.copy()
    feature_count = 0

    # ============== MOMENTUM FEATURES ==============
    if 'Absolute Returns - 3M' in df.columns and 'Absolute Returns - 6M' in df.columns:
        df['Momentum_3M_6M'] = df['Absolute Returns - 3M'] / (df['Absolute Returns - 6M'] + 0.01)
        df['Momentum_Strength'] = df['Absolute Returns - 3M'] * np.exp(-df['Volatility']/100)

        momentum_cols = ['Absolute Returns - 3M', 'Absolute Returns - 6M', 'Absolute Returns - 1Y']
        available_mom = [c for c in momentum_cols if c in df.columns]
        if len(available_mom) > 1:
            df['Momentum_Consistency'] = df[available_mom].std(axis=1) / (df[available_mom].mean(axis=1) + 0.01)
            df['Momentum_Trend'] = np.gradient(df[available_mom].values, axis=1).mean(axis=1)
        feature_count += 4

    # ============== RISK-ADJUSTED METRICS ==============
    if 'Sharpe Ratio' in df.columns:
        df['Enhanced_Sharpe'] = df['Sharpe Ratio'] * (1 + df.get('Alpha', 0)/100)
        df['Sharpe_Percentile'] = df['Sharpe Ratio'].rank(pct=True)
        feature_count += 2

    if 'Sortino Ratio' in df.columns and 'Sharpe Ratio' in df.columns:
        df['Downside_Protection_Ratio'] = df['Sortino Ratio'] / (df['Sharpe Ratio'] + 0.01)
        df['Risk_Asymmetry'] = df['Sortino Ratio'] - df['Sharpe Ratio']
        feature_count += 2

    # ============== ALPHA PERSISTENCE ==============
    if 'Alpha' in df.columns:
        df['Alpha_Squared'] = df['Alpha'] ** 2
        df['Alpha_Rank'] = df['Alpha'].rank(pct=True)
        df['Super_Alpha'] = (df['Alpha'] > df['Alpha'].quantile(0.9)).astype(int)
        feature_count += 3

    # ============== SMART BETA FACTORS ==============
    if 'PE Ratio' in df.columns and 'Category PE Ratio' in df.columns:
        df['Value_Factor'] = (df['Category PE Ratio'] - df['PE Ratio']) / df['Category PE Ratio']
        df['Deep_Value'] = (df['PE Ratio'] < df['Category PE Ratio'] * 0.7).astype(int)
        feature_count += 2

    if '% Largecap Holding' in df.columns:
        df['Quality_Score'] = df['% Largecap Holding'] * 0.6
    if 'Maximum Drawdown' in df.columns:
        df['Drawdown_Control'] = 1 / (abs(df['Maximum Drawdown']) + 1)
    feature_count += 2

    if 'AUM' in df.columns:
        df['Size_Factor'] = np.log1p(df['AUM'])
        df['AUM_Growth_Potential'] = df['AUM'].rank(pct=True)
        df['Optimal_Size'] = ((df['AUM'] > df['AUM'].quantile(0.2)) &
                              (df['AUM'] < df['AUM'].quantile(0.8))).astype(int)
        feature_count += 3

    # ============== PORTFOLIO CONCENTRATION ==============
    if '% Concentration - Top 3 Holdings' in df.columns:
        df['Diversification_Score'] = 100 - df['% Concentration - Top 3 Holdings']
        df['Over_Diversified'] = (df['% Concentration - Top 3 Holdings'] < 15).astype(int)
        df['Focused_Portfolio'] = (df['% Concentration - Top 3 Holdings'] > 30).astype(int)
        feature_count += 3

    # ============== EXPENSE EFFICIENCY ==============
    if 'Expense Ratio' in df.columns:
        df['Cost_Efficiency'] = 1 / (df['Expense Ratio'] + 0.01)
        df['Low_Cost_Advantage'] = (df['Expense Ratio'] < df['Expense Ratio'].quantile(0.25)).astype(int)

        if 'Alpha' in df.columns:
            df['Value_For_Money'] = df['Alpha'] / (df['Expense Ratio'] + 0.01)
        feature_count += 3

    # ============== CATEGORY LEADERSHIP ==============
    cat_outperform_cols = ['Returns vs sub-category - 1Y', 'Returns vs sub-category - 3Y',
                           'Returns vs sub-category - 5Y', 'Returns vs sub-category - 10Y']
    available_cat = [c for c in cat_outperform_cols if c in df.columns]

    if available_cat:
        df['Category_Outperformance_Mean'] = df[available_cat].mean(axis=1)
        df['Category_Consistency'] = (df[available_cat] > 0).sum(axis=1) / len(available_cat)
        df['Category_Leader'] = (df['Category_Outperformance_Mean'] >
                                 df['Category_Outperformance_Mean'].quantile(0.75)).astype(int)
        feature_count += 3

    # ============== REGIME ADAPTABILITY ==============
    if 'Volatility' in df.columns and 'Sharpe Ratio' in df.columns:
        df['All_Weather_Score'] = df['Sharpe Ratio'] / (df['Volatility'] + 1)
        df['Regime_Adaptability'] = df['Sharpe Ratio'] * np.exp(-df['Volatility']/50)
        feature_count += 2

    # ============== RECOVERY METRICS ==============
    if 'Maximum Drawdown' in df.columns and '% Away from ATH' in df.columns:
        df['Recovery_Speed'] = -df['% Away from ATH'] / (abs(df['Maximum Drawdown']) + 0.01)
        df['Near_ATH'] = (df['% Away from ATH'] > -5).astype(int)
        feature_count += 2

    # ============== COMPOSITE QUANTUM SCORE ==============
    quantum_features = []
    weights = {}

    if 'Enhanced_Sharpe' in df.columns:
        quantum_features.append('Enhanced_Sharpe')
        weights['Enhanced_Sharpe'] = 0.15

    if 'Alpha_Rank' in df.columns:
        quantum_features.append('Alpha_Rank')
        weights['Alpha_Rank'] = 0.15

    if 'Momentum_Strength' in df.columns:
        quantum_features.append('Momentum_Strength')
        weights['Momentum_Strength'] = 0.10

    if 'Category_Consistency' in df.columns:
        quantum_features.append('Category_Consistency')
        weights['Category_Consistency'] = 0.10

    if 'Cost_Efficiency' in df.columns:
        quantum_features.append('Cost_Efficiency')
        weights['Cost_Efficiency'] = 0.10

    if 'All_Weather_Score' in df.columns:
        quantum_features.append('All_Weather_Score')
        weights['All_Weather_Score'] = 0.10

    if 'Value_Factor' in df.columns:
        quantum_features.append('Value_Factor')
        weights['Value_Factor'] = 0.10

    if 'Diversification_Score' in df.columns:
        quantum_features.append('Diversification_Score')
        weights['Diversification_Score'] = 0.05

    if 'Recovery_Speed' in df.columns:
        quantum_features.append('Recovery_Speed')
        weights['Recovery_Speed'] = 0.05

    if 'Regime_Adaptability' in df.columns:
        quantum_features.append('Regime_Adaptability')
        weights['Regime_Adaptability'] = 0.10

    # Calculate Quantum Score
    if quantum_features:
        scaler = RobustScaler()
        normalized = pd.DataFrame(
            scaler.fit_transform(df[quantum_features].fillna(0)),
            columns=quantum_features,
            index=df.index
        )

        df['QUANTUM_SCORE'] = sum(
            normalized[feat] * weights.get(feat, 0.1) for feat in quantum_features
        )

        df['QUANTUM_SCORE'] = MinMaxScaler(feature_range=(0, 100)).fit_transform(
            df[['QUANTUM_SCORE']]
        ).flatten()

        df['QUANTUM_TIER'] = pd.qcut(df['QUANTUM_SCORE'], q=5,
                                      labels=['Poor', 'Below Avg', 'Average', 'Good', 'Excellent'])
        feature_count += 2

    print(f"✅ Created {feature_count} quantum predictive features")

    return df


def detect_market_regime(df: pd.DataFrame) -> tuple:
    """Advanced market regime detection with multiple indicators"""

    print("\n🌐 ADVANCED MARKET REGIME DETECTION...")

    regime_signals = {}

    if 'Absolute Returns - 3M' in df.columns:
        recent_returns = df['Absolute Returns - 3M'].dropna()
        mean_return = recent_returns.mean()
        median_return = recent_returns.median()
        skewness = recent_returns.skew()

        regime_signals['mean_return'] = mean_return
        regime_signals['median_return'] = median_return
        regime_signals['skewness'] = skewness

        print(f"  • Mean 3M Return: {mean_return:.2f}%")
        print(f"  • Median 3M Return: {median_return:.2f}%")
        print(f"  • Skewness: {skewness:.2f}")

    if 'Volatility' in df.columns:
        avg_volatility = df['Volatility'].mean()
        regime_signals['volatility'] = avg_volatility
        print(f"  • Average Volatility: {avg_volatility:.2f}")

    if '% Equity Holding' in df.columns:
        equity_allocation = df['% Equity Holding'].mean()
        regime_signals['risk_appetite'] = equity_allocation
        print(f"  • Average Equity Allocation: {equity_allocation:.1f}%")

    if 'Absolute Returns - 1Y' in df.columns:
        positive_returns = (df['Absolute Returns - 1Y'] > 0).mean()
        regime_signals['market_breadth'] = positive_returns
        print(f"  • % Funds with Positive 1Y Returns: {positive_returns*100:.1f}%")

    regime_score = 0
    regime_factors = []

    if 'mean_return' in regime_signals:
        if regime_signals['mean_return'] > 5:
            regime_score += 2
            regime_factors.append("Strong Returns")
        elif regime_signals['mean_return'] > 0:
            regime_score += 1
            regime_factors.append("Positive Returns")
        elif regime_signals['mean_return'] < -5:
            regime_score -= 2
            regime_factors.append("Negative Returns")
        else:
            regime_score -= 1
            regime_factors.append("Weak Returns")

    if 'volatility' in regime_signals:
        if regime_signals['volatility'] < 10:
            regime_score += 1
            regime_factors.append("Low Volatility")
        elif regime_signals['volatility'] > 20:
            regime_score -= 1
            regime_factors.append("High Volatility")

    if 'market_breadth' in regime_signals:
        if regime_signals['market_breadth'] > 0.7:
            regime_score += 1
            regime_factors.append("Broad Participation")
        elif regime_signals['market_breadth'] < 0.3:
            regime_score -= 1
            regime_factors.append("Narrow Market")

    if regime_score >= 3:
        regime = "STRONG BULL"
        strategy = "Maximum Aggression - Small/Mid Caps, Sectoral, High Beta"
    elif regime_score >= 1:
        regime = "BULL"
        strategy = "Growth Focus - Flexi Cap, Balanced Advantage"
    elif regime_score >= -1:
        regime = "NEUTRAL"
        strategy = "Balanced - Multi Asset, Hybrid, Large Cap"
    elif regime_score >= -3:
        regime = "BEAR"
        strategy = "Defensive - Debt, Gold, Low Volatility Equity"
    else:
        regime = "STRONG BEAR"
        strategy = "Capital Preservation - Liquid, Overnight, Arbitrage"

    print(f"\n🎯 MARKET REGIME: {regime}")
    print(f"📊 Regime Score: {regime_score}")
    print(f"📌 Key Factors: {', '.join(regime_factors)}")
    print(f"💡 Recommended Strategy: {strategy}")

    return regime, regime_score, strategy


def build_ml_models(df: pd.DataFrame, target_horizon: str = '1Y') -> tuple:
    """Builds advanced stacked ML ensemble for superior predictions"""

    print(f"\n🤖 BUILDING STACKED ML ENSEMBLE FOR {target_horizon}...")

    base_features = [
        'Sharpe Ratio', 'Sortino Ratio', 'Alpha', 'Volatility', 'Maximum Drawdown',
        'Expense Ratio', '3Y Avg Annual Rolling Return'
    ]

    quantum_features = [
        'QUANTUM_SCORE', 'Enhanced_Sharpe', 'Alpha_Rank', 'Momentum_Strength',
        'Category_Consistency', 'All_Weather_Score', 'Regime_Adaptability',
        'Value_Factor', 'Diversification_Score', 'Cost_Efficiency'
    ]

    all_features = base_features + quantum_features
    available_features = [f for f in all_features if f in df.columns]

    if len(available_features) < 5:
        print("⚠️ Insufficient features for ML. Using rule-based scoring.")
        return None, available_features

    target_map = {
        '1Y': 'Absolute Returns - 1Y',
        '3Y': 'CAGR 3Y',
        '5Y': 'CAGR 5Y'
    }

    target_col = target_map.get(target_horizon, 'Absolute Returns - 1Y')
    if target_col not in df.columns:
        for alt_target in ['Absolute Returns - 1Y', 'CAGR 3Y', '3Y Avg Annual Rolling Return']:
            if alt_target in df.columns:
                target_col = alt_target
                break

    model_df = df[available_features + [target_col]].dropna()

    if len(model_df) < 100:
        print(f"⚠️ Only {len(model_df)} samples. Results may be less reliable.")

    X = model_df[available_features]
    y = model_df[target_col]

    if len(X) >= 50:
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42,
                stratify=pd.qcut(y, q=min(5, len(X)//10), labels=False, duplicates='drop')
            )
        except:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    print(f"📊 Training on {len(X_train)} samples, testing on {len(X_test)} samples")

    models = {}

    models['rf'] = RandomForestRegressor(
        n_estimators=200, max_depth=15, min_samples_split=5,
        min_samples_leaf=2, random_state=42, n_jobs=-1
    )

    models['gb'] = GradientBoostingRegressor(
        n_estimators=150, max_depth=7, learning_rate=0.05,
        subsample=0.8, random_state=42
    )

    models['et'] = ExtraTreesRegressor(
        n_estimators=200, max_depth=15, random_state=42, n_jobs=-1
    )

    if HAS_XGB:
        models['xgb'] = xgb.XGBRegressor(
            n_estimators=150, max_depth=7, learning_rate=0.05,
            subsample=0.8, random_state=42, verbosity=0
        )

    if HAS_LGB:
        models['lgb'] = lgb.LGBMRegressor(
            n_estimators=150, max_depth=7, learning_rate=0.05,
            subsample=0.8, random_state=42, verbosity=-1
        )

    predictions = {}
    scores = {}

    for name, model in models.items():
        print(f"  Training {name.upper()}...", end='')
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        score = r2_score(y_test, pred)
        predictions[name] = pred
        scores[name] = score
        print(f" R²={score:.3f}")

    total_score = sum(scores.values())
    weights = {name: score/total_score for name, score in scores.items()}

    stacked_pred = sum(predictions[name] * weights[name] for name in predictions)
    stacked_r2 = r2_score(y_test, stacked_pred)
    stacked_rmse = np.sqrt(mean_squared_error(y_test, stacked_pred))

    print(f"\n🎯 STACKED MODEL PERFORMANCE:")
    print(f"  • R² Score: {stacked_r2:.3f}")
    print(f"  • RMSE: {stacked_rmse:.2f}%")
    print(f"  • Mean Absolute Error: {np.mean(np.abs(y_test - stacked_pred)):.2f}%")

    def ensemble_predict(X_new):
        """Predicts using the stacked ensemble"""
        preds = {}
        for name, model in models.items():
            preds[name] = model.predict(X_new)
        result = sum(preds[name] * weights[name] for name in preds)
        return result

    ensemble = {
        'models': models,
        'weights': weights,
        'features': available_features,
        'performance': {'r2': stacked_r2, 'rmse': stacked_rmse}
    }

    return ensemble_predict, ensemble


def optimize_portfolio(df: pd.DataFrame, selected_funds: List[str], risk_tolerance: str = 'balanced') -> Dict:
    """Optimizes portfolio allocation using modern portfolio theory"""

    print("\n💼 OPTIMIZING PORTFOLIO ALLOCATION...")

    if len(selected_funds) < 2:
        print("  Need at least 2 funds for optimization")
        return {selected_funds[0]: 1.0} if selected_funds else {}

    return_cols = ['Absolute Returns - 1Y', 'CAGR 3Y', '3Y Avg Annual Rolling Return']
    available_return_col = None

    for col in return_cols:
        if col in df.columns:
            available_return_col = col
            break

    if not available_return_col:
        print("  No return data available for optimization")
        return {fund: 1.0/len(selected_funds) for fund in selected_funds}

    portfolio_df = df[df['Name'].isin(selected_funds)]
    returns = portfolio_df.set_index('Name')[available_return_col].to_dict()
    volatilities = portfolio_df.set_index('Name')['Volatility'].to_dict() if 'Volatility' in df.columns else {}
    sharpe_ratios = portfolio_df.set_index('Name')['Sharpe Ratio'].to_dict() if 'Sharpe Ratio' in df.columns else {}

    risk_params = {
        'aggressive': {'target_return': 20, 'risk_weight': 0.3},
        'balanced': {'target_return': 12, 'risk_weight': 0.5},
        'conservative': {'target_return': 8, 'risk_weight': 0.7}
    }

    params = risk_params[risk_tolerance]
    n_funds = len(selected_funds)

    if sharpe_ratios and volatilities:
        scores = {}
        for fund in selected_funds:
            sharpe = sharpe_ratios.get(fund, 0.5)
            vol = volatilities.get(fund, 15)
            ret = returns.get(fund, 10)
            score = (sharpe * 0.4) + (ret / 100 * 0.3) + ((30 - vol) / 30 * 0.3)
            scores[fund] = max(score, 0.1)

        total_score = sum(scores.values())
        allocations = {fund: score/total_score for fund, score in scores.items()}

        if risk_tolerance == 'conservative':
            max_alloc = 0.30
        elif risk_tolerance == 'balanced':
            max_alloc = 0.40
        else:
            max_alloc = 0.50

        for fund in allocations:
            if allocations[fund] > max_alloc:
                excess = allocations[fund] - max_alloc
                allocations[fund] = max_alloc
                other_funds = [f for f in allocations if f != fund]
                for other in other_funds:
                    allocations[other] += excess / len(other_funds)
    else:
        allocations = {fund: 1.0/n_funds for fund in selected_funds}

    print("\n📊 OPTIMIZED ALLOCATION:")
    for fund, weight in sorted(allocations.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {fund[:50]}: {weight*100:.1f}%")

    return allocations


def create_recommendations(df: pd.DataFrame, regime_score: int) -> Dict[str, pd.DataFrame]:
    """Create risk-based fund recommendations"""

    print("\n" + "="*100)
    print(" "*35 + "💰 CREATING RECOMMENDATIONS 💰")
    print("="*100)

    results = {}

    risk_profiles = {
        'conservative': {
            'volatility_cap': 8,
            'min_sharpe': 0.8,
            'categories': ['Debt:', 'Arbitrage', 'Conservative Hybrid', 'Liquid', 'Overnight']
        },
        'balanced': {
            'volatility_cap': 15,
            'min_sharpe': 0.6,
            'categories': ['Balanced', 'Large Cap', 'Multi Asset', 'Flexi Cap']
        },
        'aggressive': {
            'volatility_cap': 100,
            'min_sharpe': 0.4,
            'categories': ['Small Cap', 'Mid Cap', 'Sectoral', 'International', 'Thematic']
        }
    }

    for risk_level, params in risk_profiles.items():
        print(f"\n{'='*80}")
        print(f"{risk_level.upper()} PORTFOLIO")
        print('='*80)

        filtered = df.copy()

        if 'Volatility' in filtered.columns:
            filtered = filtered[filtered['Volatility'] <= params['volatility_cap']]

        if 'Sharpe Ratio' in filtered.columns:
            filtered = filtered[filtered['Sharpe Ratio'] >= params['min_sharpe']]

        if 'Sub Category' in filtered.columns:
            category_mask = filtered['Sub Category'].apply(
                lambda x: any(cat in str(x) for cat in params['categories'])
            )
            filtered_category = filtered[category_mask]
            if len(filtered_category) > 0:
                filtered = filtered_category

        sort_col = 'MASTER_PREDICTION' if 'MASTER_PREDICTION' in filtered.columns else 'QUANTUM_SCORE'
        if sort_col in filtered.columns:
            filtered = filtered.sort_values(sort_col, ascending=False)

        top_funds = filtered.head(10)
        results[risk_level] = top_funds

        if not top_funds.empty:
            print("\n🏆 TOP 5 FUNDS:")
            for idx, (_, fund) in enumerate(top_funds.head(5).iterrows(), 1):
                print(f"\n{idx}. {fund['Name']}")
                print(f"   Category: {fund.get('Sub Category', 'N/A')}")
                if 'MASTER_PREDICTION' in fund.index:
                    print(f"   Predicted Return: {fund['MASTER_PREDICTION']:.2f}%")
                print(f"   Quantum Score: {fund.get('QUANTUM_SCORE', 0):.1f}/100")
                print(f"   Sharpe Ratio: {fund.get('Sharpe Ratio', 0):.2f}")
                print(f"   Expense Ratio: {fund.get('Expense Ratio', 0):.2f}%")

    return results


# ============================================================================
# AGENTIC IMPLEMENTATION (Only if ADK is available)
# ============================================================================

if ADK_AVAILABLE:

    # Configure Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')


    # ============================================================================
    # AGENT DEFINITIONS
    # ============================================================================

    class DataAgent(Agent):
        """Agent responsible for data loading and preprocessing"""

        name = "DataAgent"
        instructions = """
        You are a data specialist agent. Your responsibilities:
        1. Load mutual fund data from CSV files or DataFrames
        2. Validate data quality and structure
        3. Clean and preprocess the data
        4. Report data statistics and quality metrics

        Use the available tools to accomplish these tasks.
        """

        @tool
        def load_data(self, csv_path: str) -> str:
            """Load and validate mutual fund data from CSV"""
            try:
                df = load_and_validate_data(csv_path)
                self.context['raw_df'] = df
                return f"✅ Successfully loaded {len(df)} funds with {len(df.columns)} features"
            except Exception as e:
                return f"❌ Error loading data: {str(e)}"


    class FeatureAgent(Agent):
        """Agent responsible for feature engineering"""

        name = "FeatureAgent"
        instructions = """
        You are a financial feature engineering specialist. Your responsibilities:
        1. Create advanced quantum features from raw fund data
        2. Calculate momentum indicators and smart beta factors
        3. Detect market regime and recommend strategy
        4. Generate quantum scores for all funds

        Use the available tools to accomplish these tasks.
        """

        @tool
        def create_features(self) -> str:
            """Engineer quantum features from the loaded data"""
            try:
                df = self.context.get('raw_df')
                if df is None:
                    return "❌ No data loaded. Please load data first."

                df_features = engineer_quantum_features(df)
                self.context['featured_df'] = df_features
                return f"✅ Successfully engineered features. Dataset now has {len(df_features.columns)} features"
            except Exception as e:
                return f"❌ Error creating features: {str(e)}"

        @tool
        def detect_regime(self) -> str:
            """Detect current market regime"""
            try:
                df = self.context.get('featured_df') or self.context.get('raw_df')
                if df is None:
                    return "❌ No data available"

                regime, score, strategy = detect_market_regime(df)
                self.context['regime'] = regime
                self.context['regime_score'] = score
                self.context['strategy'] = strategy
                return f"✅ Market Regime: {regime}, Score: {score}, Strategy: {strategy}"
            except Exception as e:
                return f"❌ Error detecting regime: {str(e)}"


    class MLAgent(Agent):
        """Agent responsible for ML predictions"""

        name = "MLAgent"
        instructions = """
        You are a machine learning specialist. Your responsibilities:
        1. Build stacked ensemble ML models
        2. Generate predictions for different time horizons
        3. Evaluate model performance
        4. Create master predictions combining multiple horizons

        Use the available tools to accomplish these tasks.
        """

        @tool
        def train_and_predict(self, horizons: str = "1Y,3Y,5Y") -> str:
            """Train ML models and generate predictions"""
            try:
                df = self.context.get('featured_df')
                if df is None:
                    return "❌ No featured data available"

                horizon_list = horizons.split(',')
                predictions = {}

                for horizon in horizon_list:
                    predictor, ensemble = build_ml_models(df, horizon.strip())

                    if predictor is not None:
                        feature_df = df[ensemble['features']].fillna(0)
                        df[f'PREDICTED_{horizon}_RETURN'] = predictor(feature_df)
                        predictions[horizon] = df[f'PREDICTED_{horizon}_RETURN']

                if predictions:
                    pred_cols = [f'PREDICTED_{h}_RETURN' for h in horizon_list if f'PREDICTED_{h}_RETURN' in df.columns]
                    if pred_cols:
                        weights = [0.5, 0.3, 0.2][:len(pred_cols)]
                        df['MASTER_PREDICTION'] = sum(
                            df[col] * w for col, w in zip(pred_cols, weights)
                        )

                if 'MASTER_PREDICTION' in df.columns and 'Volatility' in df.columns:
                    df['RISK_ADJUSTED_PREDICTION'] = df['MASTER_PREDICTION'] / (df['Volatility'] + 1)

                self.context['predicted_df'] = df
                return f"✅ Successfully created predictions for {len(predictions)} horizons"
            except Exception as e:
                return f"❌ Error in ML predictions: {str(e)}"


    class PortfolioAgent(Agent):
        """Agent responsible for portfolio optimization"""

        name = "PortfolioAgent"
        instructions = """
        You are a portfolio optimization specialist. Your responsibilities:
        1. Create risk-based fund recommendations (conservative, balanced, aggressive)
        2. Optimize portfolio allocations
        3. Identify special opportunities (hidden gems, value picks, etc.)
        4. Generate actionable investment recommendations

        Use the available tools to accomplish these tasks.
        """

        @tool
        def create_fund_recommendations(self) -> str:
            """Create risk-based recommendations"""
            try:
                df = self.context.get('predicted_df')
                regime_score = self.context.get('regime_score', 0)

                if df is None:
                    return "❌ No prediction data available"

                recommendations = create_recommendations(df, regime_score)
                self.context['recommendations'] = recommendations
                self.context['final_df'] = df

                return f"✅ Created recommendations for {len(recommendations)} risk profiles"
            except Exception as e:
                return f"❌ Error creating recommendations: {str(e)}"

        @tool
        def optimize_allocation(self, risk_profile: str = "balanced", num_funds: int = 5) -> str:
            """Optimize portfolio allocation for a given risk profile"""
            try:
                recommendations = self.context.get('recommendations', {})
                df = self.context.get('final_df')

                if not recommendations or df is None:
                    return "❌ No recommendations available"

                if risk_profile not in recommendations:
                    return f"❌ Invalid risk profile. Choose from: {list(recommendations.keys())}"

                top_funds = recommendations[risk_profile].head(num_funds)
                selected_funds = top_funds['Name'].tolist()

                allocations = optimize_portfolio(df, selected_funds, risk_profile)

                return f"✅ Optimized allocation for {len(allocations)} funds in {risk_profile} portfolio"
            except Exception as e:
                return f"❌ Error optimizing allocation: {str(e)}"


    class OrchestratorAgent(Agent):
        """Main orchestrator agent that coordinates the entire analysis"""

        name = "MutualFundOrchestrator"
        instructions = """
        You are the main orchestrator for mutual fund profit maximization analysis.

        Your workflow:
        1. Use DataAgent to load and validate data
        2. Use FeatureAgent to engineer features and detect market regime
        3. Use MLAgent to build models and generate predictions
        4. Use PortfolioAgent to create recommendations and optimize allocations

        Coordinate these agents to provide comprehensive analysis and recommendations.
        Always provide clear, actionable insights to the user.
        """

        agents = [DataAgent, FeatureAgent, MLAgent, PortfolioAgent]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.context = {}


    # ============================================================================
    # MAIN AGENTIC INTERFACE
    # ============================================================================

    def run_agentic_analysis(csv_path: str, gemini_api_key: str = None):
        """
        Run the full agentic mutual fund analysis

        Parameters:
        -----------
        csv_path : str
            Path to the mutual fund CSV file
        gemini_api_key : str, optional
            Google Gemini API key for the agents

        Returns:
        --------
        AnalysisResult
            Complete analysis results
        """

        if gemini_api_key:
            os.environ['GEMINI_API_KEY'] = gemini_api_key

        print("\n" + "="*100)
        print(" "*30 + "🚀 AGENTIC MUTUAL FUND ANALYZER 🚀")
        print(" "*35 + "(Powered by Google ADK)")
        print("="*100)

        # Initialize the orchestrator
        orchestrator = OrchestratorAgent()
        runner = DirectRunner()

        # Define the analysis workflow
        workflow = f"""
        Please perform a comprehensive mutual fund analysis on the data at: {csv_path}

        Follow these steps:
        1. Load and validate the data
        2. Engineer quantum features and detect market regime
        3. Build ML models and generate predictions
        4. Create risk-based recommendations and optimize portfolios

        Provide a summary of findings and actionable recommendations.
        """

        # Run the analysis
        result = runner.run(orchestrator, workflow)

        # Extract results from context
        final_df = orchestrator.context.get('final_df')
        recommendations = orchestrator.context.get('recommendations', {})
        regime = orchestrator.context.get('regime', 'UNKNOWN')
        regime_score = orchestrator.context.get('regime_score', 0)
        strategy = orchestrator.context.get('strategy', 'N/A')

        # Save results
        if final_df is not None:
            output_file = 'agentic_profit_maximizer_results.xlsx'
            with pd.ExcelWriter(output_file) as writer:
                final_df.to_excel(writer, sheet_name='Full_Analysis', index=False)

                for risk_level, funds in recommendations.items():
                    if not funds.empty:
                        cols = ['Name', 'Sub Category', 'QUANTUM_SCORE', 'MASTER_PREDICTION',
                               'Sharpe Ratio', 'Expense Ratio']
                        available_cols = [c for c in cols if c in funds.columns]
                        funds[available_cols].to_excel(
                            writer, sheet_name=f'Top_{risk_level}', index=False
                        )

            print(f"\n✅ Results saved to {output_file}")

        print("\n" + "="*100)
        print(" "*25 + "🏁 AGENTIC ANALYSIS COMPLETE 🏁")
        print("="*100)

        return AnalysisResult(
            df=final_df,
            predictions={},
            recommendations=recommendations,
            regime=regime,
            regime_score=regime_score,
            strategy=strategy
        )

else:
    def run_agentic_analysis(csv_path: str, gemini_api_key: str = None):
        """Fallback function when ADK is not available"""
        print("❌ Google ADK is not installed. Please install it with:")
        print("   pip install google-adk")
        return None


# ============================================================================
# STANDALONE EXECUTION
# ============================================================================

def main():
    """Main execution function"""

    import sys

    if len(sys.argv) < 2:
        print("Usage: python agentic_mutual_fund_analyzer.py <csv_file> [gemini_api_key]")
        print("\nExample:")
        print("  python agentic_mutual_fund_analyzer.py real_mutual_funds.csv")
        print("  python agentic_mutual_fund_analyzer.py real_mutual_funds.csv YOUR_API_KEY")
        return

    csv_file = sys.argv[1]
    api_key = sys.argv[2] if len(sys.argv) > 2 else os.getenv('GEMINI_API_KEY')

    if ADK_AVAILABLE:
        if not api_key:
            print("⚠️ No Gemini API key provided. Set GEMINI_API_KEY environment variable or pass as argument.")
            print("   Get your API key from: https://ai.google.dev/")
            return

        result = run_agentic_analysis(csv_file, api_key)

        if result:
            print("\n📊 ANALYSIS SUMMARY:")
            print(f"  • Market Regime: {result.regime}")
            print(f"  • Regime Score: {result.regime_score}")
            print(f"  • Strategy: {result.strategy}")
            print(f"  • Total Funds Analyzed: {len(result.df) if result.df is not None else 0}")
            print(f"  • Recommendations Generated: {len(result.recommendations)}")
    else:
        print("\n⚠️ Running in NON-AGENTIC mode (ADK not available)")
        print("Installing Google ADK...")
        os.system("pip install google-adk")
        print("\nPlease run the script again after installation.")


if __name__ == "__main__":
    main()
