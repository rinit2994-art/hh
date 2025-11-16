"""CSV Data Agent - Handles CSV file operations and data analysis."""

from google.adk.agents import LlmAgent
from typing import Dict, List, Any, Optional
import pandas as pd
import os
import json


def read_csv_file(file_path: str, rows: Optional[int] = None) -> Dict[str, Any]:
    """
    Read CSV file and return its contents.

    Args:
        file_path: Path to the CSV file
        rows: Number of rows to read (None for all rows)

    Returns:
        Dictionary containing CSV data and metadata
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        df = pd.read_csv(file_path, nrows=rows)

        return {
            "file_path": file_path,
            "rows": len(df),
            "columns": list(df.columns),
            "data": df.to_dict(orient='records'),
            "preview": df.head(10).to_dict(orient='records'),
            "dtypes": df.dtypes.astype(str).to_dict()
        }
    except Exception as e:
        return {"error": f"Failed to read CSV file: {str(e)}"}


def get_csv_summary(file_path: str) -> Dict[str, Any]:
    """
    Get summary statistics of CSV file.

    Args:
        file_path: Path to the CSV file

    Returns:
        Dictionary containing summary statistics
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        df = pd.read_csv(file_path)

        # Get numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        summary = {
            "file_path": file_path,
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "numeric_columns": numeric_cols,
            "missing_values": df.isnull().sum().to_dict(),
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"
        }

        # Add statistics for numeric columns
        if numeric_cols:
            summary["statistics"] = df[numeric_cols].describe().to_dict()

        return summary
    except Exception as e:
        return {"error": f"Failed to get CSV summary: {str(e)}"}


def filter_csv_data(file_path: str, column: str, value: Any, operator: str = "equals") -> Dict[str, Any]:
    """
    Filter CSV data based on column value.

    Args:
        file_path: Path to the CSV file
        column: Column name to filter on
        value: Value to filter by
        operator: Comparison operator (equals, greater_than, less_than, contains)

    Returns:
        Dictionary containing filtered data
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        df = pd.read_csv(file_path)

        if column not in df.columns:
            return {"error": f"Column '{column}' not found in CSV"}

        # Apply filter based on operator
        if operator == "equals":
            filtered_df = df[df[column] == value]
        elif operator == "greater_than":
            filtered_df = df[df[column] > value]
        elif operator == "less_than":
            filtered_df = df[df[column] < value]
        elif operator == "contains":
            filtered_df = df[df[column].astype(str).str.contains(str(value), na=False)]
        else:
            return {"error": f"Unknown operator: {operator}"}

        return {
            "file_path": file_path,
            "filter": f"{column} {operator} {value}",
            "matched_rows": len(filtered_df),
            "data": filtered_df.to_dict(orient='records')
        }
    except Exception as e:
        return {"error": f"Failed to filter CSV data: {str(e)}"}


def aggregate_csv_data(file_path: str, group_by: str, agg_column: str, operation: str = "mean") -> Dict[str, Any]:
    """
    Aggregate CSV data by grouping.

    Args:
        file_path: Path to the CSV file
        group_by: Column to group by
        agg_column: Column to aggregate
        operation: Aggregation operation (mean, sum, count, min, max)

    Returns:
        Dictionary containing aggregated data
    """
    try:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}

        df = pd.read_csv(file_path)

        if group_by not in df.columns:
            return {"error": f"Group by column '{group_by}' not found"}

        if agg_column not in df.columns:
            return {"error": f"Aggregate column '{agg_column}' not found"}

        # Perform aggregation
        if operation == "mean":
            result = df.groupby(group_by)[agg_column].mean()
        elif operation == "sum":
            result = df.groupby(group_by)[agg_column].sum()
        elif operation == "count":
            result = df.groupby(group_by)[agg_column].count()
        elif operation == "min":
            result = df.groupby(group_by)[agg_column].min()
        elif operation == "max":
            result = df.groupby(group_by)[agg_column].max()
        else:
            return {"error": f"Unknown operation: {operation}"}

        return {
            "file_path": file_path,
            "operation": f"{operation} of {agg_column} grouped by {group_by}",
            "results": result.to_dict()
        }
    except Exception as e:
        return {"error": f"Failed to aggregate CSV data: {str(e)}"}


def write_csv_file(file_path: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Write data to a CSV file.

    Args:
        file_path: Path where CSV file will be saved
        data: List of dictionaries representing rows

    Returns:
        Dictionary containing write status
    """
    try:
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)

        return {
            "file_path": file_path,
            "rows_written": len(df),
            "columns": list(df.columns),
            "status": "success"
        }
    except Exception as e:
        return {"error": f"Failed to write CSV file: {str(e)}"}


def list_csv_files(directory: str = ".") -> Dict[str, Any]:
    """
    List all CSV files in a directory.

    Args:
        directory: Directory path to search

    Returns:
        Dictionary containing list of CSV files
    """
    try:
        if not os.path.exists(directory):
            return {"error": f"Directory not found: {directory}"}

        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]

        file_info = []
        for file in csv_files:
            file_path = os.path.join(directory, file)
            size = os.path.getsize(file_path)
            file_info.append({
                "name": file,
                "path": file_path,
                "size_kb": round(size / 1024, 2)
            })

        return {
            "directory": directory,
            "csv_files": file_info,
            "count": len(csv_files)
        }
    except Exception as e:
        return {"error": f"Failed to list CSV files: {str(e)}"}


# Create the CSV data agent
csv_agent = LlmAgent(
    name="csv_data_agent",
    model="gemini-2.0-flash-exp",
    description="I handle CSV file operations including reading, filtering, aggregating, and writing CSV data.",
    instruction="""You are a CSV data specialist. Your role is to:

    1. Read and analyze CSV files
    2. Provide summary statistics and metadata
    3. Filter and query CSV data
    4. Aggregate data with grouping operations
    5. Write data to CSV files
    6. List available CSV files in directories

    Always validate file paths and column names before performing operations.
    Provide clear error messages when something goes wrong.
    When working with large files, consider using row limits for previews.
    """,
    tools=[
        read_csv_file,
        get_csv_summary,
        filter_csv_data,
        aggregate_csv_data,
        write_csv_file,
        list_csv_files
    ]
)
