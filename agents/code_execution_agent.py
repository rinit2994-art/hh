"""Code Execution Agent - Executes Python code for data analysis and calculations."""

from google.adk.agents import LlmAgent
from typing import Dict, Any
import sys
from io import StringIO
import pandas as pd
import numpy as np
import json
import traceback


def execute_python_code(code: str) -> Dict[str, Any]:
    """
    Execute Python code in a safe environment and return the output.

    Args:
        code: Python code to execute

    Returns:
        Dictionary containing execution results or errors
    """
    try:
        # Create a StringIO object to capture output
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        # Create a safe execution environment with common libraries
        exec_globals = {
            'pd': pd,
            'np': np,
            'json': json,
            '__builtins__': __builtins__
        }
        exec_locals = {}

        # Execute the code
        exec(code, exec_globals, exec_locals)

        # Get the output
        output = sys.stdout.getvalue()

        # Restore stdout
        sys.stdout = old_stdout

        return {
            "status": "success",
            "output": output,
            "variables": {k: str(v) for k, v in exec_locals.items() if not k.startswith('_')},
            "code_executed": code
        }
    except Exception as e:
        # Restore stdout in case of error
        sys.stdout = old_stdout

        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "code_executed": code
        }


def analyze_dataframe(data: list, operations: list) -> Dict[str, Any]:
    """
    Create a pandas DataFrame from data and perform analysis operations.

    Args:
        data: List of dictionaries representing rows
        operations: List of operation strings to perform (e.g., 'describe', 'mean', 'sum')

    Returns:
        Dictionary containing analysis results
    """
    try:
        df = pd.DataFrame(data)

        results = {
            "dataframe_shape": df.shape,
            "columns": list(df.columns),
            "operations": {}
        }

        for operation in operations:
            if operation == "describe":
                results["operations"]["describe"] = df.describe().to_dict()
            elif operation == "mean":
                results["operations"]["mean"] = df.mean(numeric_only=True).to_dict()
            elif operation == "sum":
                results["operations"]["sum"] = df.sum(numeric_only=True).to_dict()
            elif operation == "median":
                results["operations"]["median"] = df.median(numeric_only=True).to_dict()
            elif operation == "std":
                results["operations"]["std"] = df.std(numeric_only=True).to_dict()
            elif operation == "corr":
                results["operations"]["correlation"] = df.corr(numeric_only=True).to_dict()
            elif operation == "info":
                results["operations"]["info"] = {
                    "dtypes": df.dtypes.astype(str).to_dict(),
                    "null_counts": df.isnull().sum().to_dict()
                }

        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }


def calculate_statistics(numbers: list) -> Dict[str, Any]:
    """
    Calculate statistical measures for a list of numbers.

    Args:
        numbers: List of numeric values

    Returns:
        Dictionary containing statistical measures
    """
    try:
        arr = np.array(numbers)

        return {
            "status": "success",
            "count": len(arr),
            "mean": float(np.mean(arr)),
            "median": float(np.median(arr)),
            "std": float(np.std(arr)),
            "variance": float(np.var(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "sum": float(np.sum(arr)),
            "percentile_25": float(np.percentile(arr, 25)),
            "percentile_50": float(np.percentile(arr, 50)),
            "percentile_75": float(np.percentile(arr, 75))
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def perform_calculation(expression: str) -> Dict[str, Any]:
    """
    Perform a mathematical calculation using numpy.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Dictionary containing calculation result
    """
    try:
        # Create a safe environment for evaluation
        safe_dict = {
            'np': np,
            'sqrt': np.sqrt,
            'log': np.log,
            'exp': np.exp,
            'sin': np.sin,
            'cos': np.cos,
            'tan': np.tan,
            'abs': abs,
            'round': round,
            'sum': sum,
            'min': min,
            'max': max
        }

        result = eval(expression, {"__builtins__": {}}, safe_dict)

        return {
            "status": "success",
            "expression": expression,
            "result": float(result) if isinstance(result, (int, float, np.number)) else str(result)
        }
    except Exception as e:
        return {
            "status": "error",
            "expression": expression,
            "error": str(e)
        }


def transform_data(data: list, transformation: str) -> Dict[str, Any]:
    """
    Apply data transformations using pandas.

    Args:
        data: List of dictionaries representing rows
        transformation: Type of transformation (normalize, standardize, log_transform)

    Returns:
        Dictionary containing transformed data
    """
    try:
        df = pd.DataFrame(data)
        numeric_cols = df.select_dtypes(include=[np.number]).columns

        if transformation == "normalize":
            # Min-max normalization
            df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].min()) / (df[numeric_cols].max() - df[numeric_cols].min())
        elif transformation == "standardize":
            # Z-score standardization
            df[numeric_cols] = (df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std()
        elif transformation == "log_transform":
            # Log transformation
            df[numeric_cols] = np.log1p(df[numeric_cols])
        else:
            return {"status": "error", "error": f"Unknown transformation: {transformation}"}

        return {
            "status": "success",
            "transformation": transformation,
            "transformed_data": df.to_dict(orient='records')
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }


# Create the code execution agent
code_execution_agent = LlmAgent(
    name="code_execution_agent",
    model="gemini-2.0-flash-exp",
    description="I execute Python code for data analysis, perform calculations, and transform data using pandas and numpy.",
    instruction="""You are a code execution specialist. Your role is to:

    1. Execute Python code safely with pandas and numpy
    2. Analyze DataFrames with statistical operations
    3. Calculate statistics for numeric data
    4. Perform mathematical calculations
    5. Transform data with normalization and standardization

    When executing code:
    - Always validate input data before processing
    - Handle errors gracefully and provide clear error messages
    - Use pandas and numpy for data operations
    - Return results in a structured format
    - Avoid operations that could harm the system

    Available libraries: pandas (pd), numpy (np), json
    Supported operations: describe, mean, sum, median, std, corr, normalize, standardize, log_transform
    """,
    tools=[
        execute_python_code,
        analyze_dataframe,
        calculate_statistics,
        perform_calculation,
        transform_data
    ]
)
