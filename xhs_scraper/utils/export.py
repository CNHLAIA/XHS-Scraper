"""JSON and CSV export utilities for scraped data."""

import csv
import json
from pathlib import Path
from typing import Any, Union

from pydantic import BaseModel


def _serialize_value(value: Any) -> Any:
    """Serialize a value for JSON/CSV export.

    Converts Pydantic models to dicts and handles nested objects.
    """
    if isinstance(value, BaseModel):
        return value.model_dump()
    elif isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_serialize_value(item) for item in value]
    else:
        return value


def _flatten_dict(data: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Flatten nested dictionary for CSV export.

    Nested dicts and lists are serialized as JSON strings.
    """
    items = []
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            # Serialize dict as JSON string
            items.append((new_key, json.dumps(v, ensure_ascii=False)))
        elif isinstance(v, list):
            # Serialize list as JSON string
            items.append((new_key, json.dumps(v, ensure_ascii=False)))
        elif isinstance(v, BaseModel):
            # Serialize Pydantic model as JSON string
            items.append((new_key, json.dumps(v.model_dump(), ensure_ascii=False)))
        else:
            items.append((new_key, v))

    return dict(items)


def _ensure_list(data: Union[list[Any], Any]) -> list[Any]:
    """Ensure data is a list."""
    if isinstance(data, list):
        return data
    else:
        return [data]


def _convert_to_dict(data: Any) -> dict:
    """Convert data to dictionary."""
    if isinstance(data, BaseModel):
        return data.model_dump()
    elif isinstance(data, dict):
        return data
    else:
        return {"data": data}


def export_to_json(
    data: Union[list[Any], Any],
    filepath: Union[str, Path],
    indent: int = 2,
) -> Path:
    """Export data to JSON file.

    Handles both single items and lists. Converts Pydantic models to dicts.

    Args:
        data: Data to export (single item or list).
        filepath: Output file path.
        indent: JSON indentation level (default: 2).

    Returns:
        Path object of the created file.

    Raises:
        IOError: If file cannot be written.
    """
    filepath = Path(filepath)

    # Create parent directories if they don't exist
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Convert data to list
    data_list = _ensure_list(data)

    # Serialize all items
    serialized_data = [_serialize_value(item) for item in data_list]

    # For single items, export as single dict (not wrapped in list)
    if len(data_list) == 1 and not isinstance(data, list):
        export_data = serialized_data[0]
    else:
        export_data = serialized_data

    # Write to JSON file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=indent)

    return filepath


def export_to_csv(
    data: Union[list[Any], Any],
    filepath: Union[str, Path],
) -> Path:
    """Export data to CSV file with flattened fields.

    Nested objects are serialized as JSON strings for CSV compatibility.
    Uses UTF-8 encoding with BOM for Excel compatibility.

    Args:
        data: Data to export (single item or list).
        filepath: Output file path.

    Returns:
        Path object of the created file.

    Raises:
        IOError: If file cannot be written.
    """
    filepath = Path(filepath)

    # Create parent directories if they don't exist
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Convert data to list
    data_list = _ensure_list(data)

    # Handle empty data
    if not data_list:
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([])
        return filepath

    # Convert all items to dicts
    dict_list = [_convert_to_dict(item) for item in data_list]

    # Flatten all dicts
    flattened_list = [_flatten_dict(d) for d in dict_list]

    # Collect all unique field names (preserve order)
    all_keys = []
    seen = set()
    for item in flattened_list:
        for key in item.keys():
            if key not in seen:
                all_keys.append(key)
                seen.add(key)

    # Write to CSV file with UTF-8 BOM for Excel compatibility
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        for item in flattened_list:
            writer.writerow(item)

    return filepath
