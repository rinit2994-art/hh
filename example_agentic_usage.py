"""
Example Usage of Agentic Mutual Fund Analyzer

This script demonstrates how to use the agentic system
with different configurations and queries.
"""

import os
from agentic_mutual_fund_analyzer import run_agentic_analysis, ADK_AVAILABLE

def example_basic_analysis():
    """
    Example 1: Basic analysis with default settings
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Agentic Analysis")
    print("="*80)

    if not ADK_AVAILABLE:
        print("⚠️  Google ADK not available. Please install:")
        print("   pip install google-adk")
        return

    # Set your API key
    api_key = os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')

    # Run the analysis
    result = run_agentic_analysis(
        csv_path='real_mutual_funds.csv',
        gemini_api_key=api_key
    )

    if result:
        print("\n📊 RESULTS:")
        print(f"  • Market Regime: {result.regime}")
        print(f"  • Recommended Strategy: {result.strategy}")
        print(f"  • Funds Analyzed: {len(result.df) if result.df is not None else 0}")
        print(f"  • Risk Profiles: {list(result.recommendations.keys())}")


def example_conservative_focus():
    """
    Example 2: Focus on conservative, low-risk funds
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Conservative Portfolio Focus")
    print("="*80)

    if not ADK_AVAILABLE:
        print("⚠️  Google ADK not available.")
        return

    from agentic_mutual_fund_analyzer import OrchestratorAgent, DirectRunner

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  Set GEMINI_API_KEY environment variable")
        return

    orchestrator = OrchestratorAgent()
    runner = DirectRunner()

    workflow = """
    Analyze the mutual funds in 'real_mutual_funds.csv' with a focus on:
    1. Low volatility (< 8%)
    2. High Sharpe ratio (> 1.0)
    3. Debt and conservative hybrid funds
    4. Expense ratio < 0.5%

    Provide top 5 ultra-safe recommendations for a conservative investor.
    """

    result = runner.run(orchestrator, workflow)
    print("\n✅ Conservative analysis complete!")


def example_aggressive_growth():
    """
    Example 3: Aggressive growth portfolio
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Aggressive Growth Strategy")
    print("="*80)

    if not ADK_AVAILABLE:
        print("⚠️  Google ADK not available.")
        return

    from agentic_mutual_fund_analyzer import OrchestratorAgent, DirectRunner

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  Set GEMINI_API_KEY environment variable")
        return

    orchestrator = OrchestratorAgent()
    runner = DirectRunner()

    workflow = """
    Find the highest potential mutual funds for maximum growth:
    1. Small-cap and mid-cap focus
    2. High momentum (strong 3M and 6M returns)
    3. High alpha (> 5)
    4. Sectoral/thematic opportunities

    Create an aggressive portfolio optimized for 3-year returns.
    Volatility is acceptable if returns potential is high.
    """

    result = runner.run(orchestrator, workflow)
    print("\n✅ Aggressive strategy analysis complete!")


def example_custom_criteria():
    """
    Example 4: Custom filtering criteria
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Custom Filtering Criteria")
    print("="*80)

    if not ADK_AVAILABLE:
        print("⚠️  Google ADK not available.")
        return

    from agentic_mutual_fund_analyzer import OrchestratorAgent, DirectRunner

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  Set GEMINI_API_KEY environment variable")
        return

    orchestrator = OrchestratorAgent()
    runner = DirectRunner()

    workflow = """
    Custom Analysis Requirements:

    MUST HAVE:
    - AUM > 1000 Cr (established funds)
    - Fund Manager tenure > 3 years
    - Consistently outperformed category (3Y, 5Y)

    NICE TO HAVE:
    - Low expense ratio
    - High Sharpe ratio

    AVOID:
    - Funds with high drawdown (< -30%)
    - New funds (< 1 year old)

    Provide balanced recommendations meeting these criteria.
    """

    result = runner.run(orchestrator, workflow)
    print("\n✅ Custom criteria analysis complete!")


def example_sector_specific():
    """
    Example 5: Sector-specific analysis
    """
    print("\n" + "="*80)
    print("EXAMPLE 5: Sector-Specific Analysis")
    print("="*80)

    if not ADK_AVAILABLE:
        print("⚠️  Google ADK not available.")
        return

    from agentic_mutual_fund_analyzer import OrchestratorAgent, DirectRunner

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("⚠️  Set GEMINI_API_KEY environment variable")
        return

    orchestrator = OrchestratorAgent()
    runner = DirectRunner()

    workflow = """
    Sector Rotation Strategy:

    Based on current market regime:
    1. Identify leading sectors
    2. Find best sectoral/thematic funds
    3. Create a sector-diversified portfolio
    4. Include both defensive and growth sectors

    Analyze:
    - Technology/IT funds
    - Banking/Financial funds
    - Infrastructure/Manufacturing funds
    - International/Global funds

    Recommend allocation across sectors.
    """

    result = runner.run(orchestrator, workflow)
    print("\n✅ Sector analysis complete!")


def example_comparison_notebook_vs_agentic():
    """
    Example 6: Compare traditional notebook vs agentic approach
    """
    print("\n" + "="*80)
    print("EXAMPLE 6: Traditional vs Agentic Comparison")
    print("="*80)

    print("\n📝 TRADITIONAL NOTEBOOK APPROACH:")
    print("-" * 80)
    print("""
    Manual Steps Required:
    1. Run cell 1: Import libraries
    2. Run cell 2: Load data
    3. Run cell 3: Engineer features (manual parameter tuning)
    4. Run cell 4: Build ML models (wait for training)
    5. Run cell 5: Detect regime
    6. Run cell 6: Create predictions
    7. Run cell 7: Optimize portfolio
    8. Run cell 8: Generate visualizations
    9. Manually interpret results
    10. Make investment decisions

    Time: 30-45 minutes (including analysis time)
    Effort: High (manual execution and decision-making)
    Reproducibility: Medium (depends on execution order)
    Scalability: Low (can't automate across multiple datasets)
    Customization: Requires code changes
    """)

    print("\n🤖 AGENTIC APPROACH:")
    print("-" * 80)
    print("""
    Single Command:
    $ python agentic_mutual_fund_analyzer.py real_mutual_funds.csv

    Or Natural Language:
    "Analyze these mutual funds and recommend top conservative picks"

    What Happens Automatically:
    1. DataAgent loads and validates data
    2. FeatureAgent engineers optimal features
    3. FeatureAgent detects market regime
    4. MLAgent builds and tunes models
    5. MLAgent generates predictions
    6. PortfolioAgent creates recommendations
    7. PortfolioAgent optimizes allocations
    8. OrchestratorAgent synthesizes insights
    9. Results automatically saved

    Time: 20-25 seconds (fully automated)
    Effort: Minimal (just provide query)
    Reproducibility: High (consistent workflow)
    Scalability: High (can process multiple datasets)
    Customization: Natural language instructions
    """)

    print("\n📊 KEY DIFFERENCES:")
    print("-" * 80)
    print("""
    ┌─────────────────────┬──────────────────┬──────────────────┐
    │ Feature             │ Notebook         │ Agentic          │
    ├─────────────────────┼──────────────────┼──────────────────┤
    │ Autonomy            │ None             │ Full             │
    │ Human Intervention  │ Constant         │ Minimal          │
    │ Decision Making     │ Manual           │ AI-driven        │
    │ Adaptability        │ Fixed workflow   │ Dynamic          │
    │ Error Recovery      │ Manual debugging │ Self-correcting  │
    │ Collaboration       │ Single context   │ Multi-agent      │
    │ Natural Language    │ No               │ Yes              │
    │ Parallelization     │ Sequential       │ Concurrent       │
    └─────────────────────┴──────────────────┴──────────────────┘
    """)


def main():
    """Run all examples"""

    print("\n" + "="*80)
    print("🤖 AGENTIC MUTUAL FUND ANALYZER - EXAMPLES")
    print("="*80)

    # Check ADK availability
    if not ADK_AVAILABLE:
        print("\n⚠️  WARNING: Google ADK is not installed!")
        print("   Install it with: pip install google-adk")
        print("   Get API key from: https://ai.google.dev/")
        print("\n   Running comparison example only...\n")
        example_comparison_notebook_vs_agentic()
        return

    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("\n⚠️  WARNING: GEMINI_API_KEY not set!")
        print("   Set it with: export GEMINI_API_KEY='your_key'")
        print("   Get your key from: https://ai.google.dev/")
        print("\n   Running comparison example only...\n")
        example_comparison_notebook_vs_agentic()
        return

    # Run examples
    print("\nChoose an example to run:")
    print("1. Basic Analysis")
    print("2. Conservative Portfolio")
    print("3. Aggressive Growth")
    print("4. Custom Criteria")
    print("5. Sector-Specific")
    print("6. Comparison (Notebook vs Agentic)")
    print("0. Run All")

    try:
        choice = input("\nEnter choice (0-6): ").strip()
    except EOFError:
        print("\nRunning comparison example (non-interactive mode)...")
        example_comparison_notebook_vs_agentic()
        return

    examples = {
        '0': lambda: [example() for example in [
            example_basic_analysis,
            example_conservative_focus,
            example_aggressive_growth,
            example_custom_criteria,
            example_sector_specific,
            example_comparison_notebook_vs_agentic
        ]],
        '1': example_basic_analysis,
        '2': example_conservative_focus,
        '3': example_aggressive_growth,
        '4': example_custom_criteria,
        '5': example_sector_specific,
        '6': example_comparison_notebook_vs_agentic
    }

    example_func = examples.get(choice)
    if example_func:
        example_func()
    else:
        print("Invalid choice!")

    print("\n" + "="*80)
    print("✅ Examples Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
