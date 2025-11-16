#!/usr/bin/env python3
"""Test script to execute the mutual fund predictor notebook"""

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import sys

def test_notebook():
    """Execute the Jupyter notebook and verify it works"""

    print("="*80)
    print("TESTING MUTUAL FUND PROFIT PREDICTOR NOTEBOOK")
    print("="*80)

    # Load the notebook
    print("\n📂 Loading notebook...")
    with open('mutual_fund_profit_predictor.ipynb', 'r') as f:
        nb = nbformat.read(f, as_version=4)

    # Execute the notebook (except the last example cells)
    print("🚀 Executing notebook cells...\n")

    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

    try:
        # Execute all cells up to the usage examples
        # We'll execute cells 0-16 (setup, functions, but not the example usage)
        cells_to_execute = nb.cells[:17]  # Up to and including cell 16

        for i, cell in enumerate(cells_to_execute):
            if cell.cell_type == 'code':
                print(f"Executing cell {i}...")
                temp_nb = nbformat.v4.new_notebook()
                temp_nb.cells = nb.cells[:i+1]
                ep.preprocess(temp_nb)
                nb.cells[i] = temp_nb.cells[i]

        print("\n✅ Notebook cells executed successfully!")
        print("\n" + "="*80)
        print("NOW TESTING WITH SAMPLE DATA")
        print("="*80)

        # Now run a test with the sample data
        test_code = '''
# Test the profit maximizer with sample data
import pandas as pd

print("\\n📊 Loading sample mutual fund data...")
df = pd.read_csv('sample_mutual_funds.csv')
print(f"Loaded {len(df)} sample funds")

print("\\n🚀 Running profit maximization analysis...")
results_df, recommendations = maximize_profits(df)

print("\\n✅ ANALYSIS COMPLETED SUCCESSFULLY!")
print(f"\\n📈 Results shape: {results_df.shape}")
print(f"\\n🎯 Generated recommendations for {len(recommendations)} risk profiles")

# Show a quick summary
if 'QUANTUM_SCORE' in results_df.columns:
    print(f"\\nQuantum Score Range: {results_df['QUANTUM_SCORE'].min():.1f} - {results_df['QUANTUM_SCORE'].max():.1f}")

if 'MASTER_PREDICTION' in results_df.columns:
    print(f"Predicted Return Range: {results_df['MASTER_PREDICTION'].min():.1f}% - {results_df['MASTER_PREDICTION'].max():.1f}%")

print("\\n" + "="*80)
print("🎉 NOTEBOOK TEST COMPLETED SUCCESSFULLY! 🎉")
print("="*80)
'''

        # Add and execute the test code
        test_cell = nbformat.v4.new_code_cell(test_code)
        nb.cells.append(test_cell)

        temp_nb = nbformat.v4.new_notebook()
        temp_nb.cells = nb.cells
        ep.preprocess(temp_nb)

        # Get the output from the last cell
        last_cell = temp_nb.cells[-1]
        if hasattr(last_cell, 'outputs'):
            for output in last_cell.outputs:
                if hasattr(output, 'text'):
                    print(output.text)
                elif hasattr(output, 'data'):
                    if 'text/plain' in output.data:
                        print(output.data['text/plain'])

        return True

    except Exception as e:
        print(f"\n❌ Error executing notebook: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_notebook()
    sys.exit(0 if success else 1)
