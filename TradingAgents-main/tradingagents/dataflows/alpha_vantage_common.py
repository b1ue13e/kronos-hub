import os
import requests
import pandas as pd
import json
from datetime import datetime
from io import StringIO
import threading
import time

API_BASE_URL = "https://www.alphavantage.co/query"
_SESSION = requests.Session()
_SESSION.trust_env = False
_REQUEST_LOCK = threading.Lock()
_RESPONSE_CACHE: dict[str, dict | str] = {}
_LAST_REQUEST_TS = 0.0
_MIN_INTERVAL_SECONDS = float(os.getenv("ALPHA_VANTAGE_MIN_INTERVAL_SECONDS", "1.2"))
_MAX_RATE_LIMIT_RETRIES = int(os.getenv("ALPHA_VANTAGE_MAX_RATE_LIMIT_RETRIES", "2"))
_RATE_LIMIT_BACKOFF_SECONDS = float(os.getenv("ALPHA_VANTAGE_RATE_LIMIT_BACKOFF_SECONDS", "15"))

def get_api_key() -> str:
    """Retrieve the API key for Alpha Vantage from environment variables."""
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY environment variable is not set.")
    return api_key

def format_datetime_for_api(date_input) -> str:
    """Convert various date formats to YYYYMMDDTHHMM format required by Alpha Vantage API."""
    if isinstance(date_input, str):
        # If already in correct format, return as-is
        if len(date_input) == 13 and 'T' in date_input:
            return date_input
        # Try to parse common date formats
        try:
            dt = datetime.strptime(date_input, "%Y-%m-%d")
            return dt.strftime("%Y%m%dT0000")
        except ValueError:
            try:
                dt = datetime.strptime(date_input, "%Y-%m-%d %H:%M")
                return dt.strftime("%Y%m%dT%H%M")
            except ValueError:
                raise ValueError(f"Unsupported date format: {date_input}")
    elif isinstance(date_input, datetime):
        return date_input.strftime("%Y%m%dT%H%M")
    else:
        raise ValueError(f"Date must be string or datetime object, got {type(date_input)}")

class AlphaVantageRateLimitError(Exception):
    """Exception raised when Alpha Vantage API rate limit is exceeded."""
    pass


def _build_cache_key(function_name: str, params: dict) -> str:
    return json.dumps(
        {
            "function": function_name,
            "params": params,
        },
        sort_keys=True,
        default=str,
    )


def _wait_for_request_slot() -> None:
    global _LAST_REQUEST_TS
    with _REQUEST_LOCK:
        now = time.monotonic()
        wait_seconds = _MIN_INTERVAL_SECONDS - (now - _LAST_REQUEST_TS)
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        _LAST_REQUEST_TS = time.monotonic()


def _make_api_request(function_name: str, params: dict) -> dict | str:
    """Helper function to make API requests and handle responses.
    
    Raises:
        AlphaVantageRateLimitError: When API rate limit is exceeded
    """
    # Create a copy of params to avoid modifying the original
    api_params = params.copy()
    api_params.update({
        "function": function_name,
        "apikey": get_api_key(),
        "source": "trading_agents",
    })
    
    # Handle entitlement parameter if present in params or global variable
    current_entitlement = globals().get('_current_entitlement')
    entitlement = api_params.get("entitlement") or current_entitlement
    
    if entitlement:
        api_params["entitlement"] = entitlement
    elif "entitlement" in api_params:
        # Remove entitlement if it's None or empty
        api_params.pop("entitlement", None)

    cache_key = _build_cache_key(function_name, api_params)
    if cache_key in _RESPONSE_CACHE:
        return _RESPONSE_CACHE[cache_key]

    for attempt in range(_MAX_RATE_LIMIT_RETRIES + 1):
        _wait_for_request_slot()
        response = _SESSION.get(API_BASE_URL, params=api_params, timeout=(10, 30))
        response.raise_for_status()

        response_text = response.text

        try:
            response_json = json.loads(response_text)
            api_message = (
                response_json.get("Information")
                or response_json.get("Note")
                or response_json.get("Error Message")
            )
            if api_message:
                lowered = api_message.lower()
                if (
                    "rate limit" in lowered
                    or "api key" in lowered
                    or "thank you for using alpha vantage" in lowered
                    or "premium" in lowered
                ):
                    if attempt < _MAX_RATE_LIMIT_RETRIES:
                        time.sleep(_RATE_LIMIT_BACKOFF_SECONDS * (attempt + 1))
                        continue
                    raise AlphaVantageRateLimitError(f"Alpha Vantage rate limit exceeded: {api_message}")
                raise ValueError(f"Alpha Vantage API error for {function_name}: {api_message}")

            if api_params.get("datatype") == "csv":
                raise ValueError(f"Unexpected JSON response for {function_name}: {response_json}")

            _RESPONSE_CACHE[cache_key] = response_json
            return response_json
        except json.JSONDecodeError:
            _RESPONSE_CACHE[cache_key] = response_text
            return response_text

    raise AlphaVantageRateLimitError("Alpha Vantage request exhausted retry budget.")



def _filter_csv_by_date_range(csv_data: str, start_date: str, end_date: str) -> str:
    """
    Filter CSV data to include only rows within the specified date range.

    Args:
        csv_data: CSV string from Alpha Vantage API
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format

    Returns:
        Filtered CSV string
    """
    if not csv_data or csv_data.strip() == "":
        return csv_data

    try:
        # Parse CSV data
        df = pd.read_csv(StringIO(csv_data))

        # Assume the first column is the date column (timestamp)
        date_col = df.columns[0]
        df[date_col] = pd.to_datetime(df[date_col])

        # Filter by date range
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)

        filtered_df = df[(df[date_col] >= start_dt) & (df[date_col] <= end_dt)]

        # Convert back to CSV string
        return filtered_df.to_csv(index=False)

    except Exception as e:
        # If filtering fails, return original data with a warning
        print(f"Warning: Failed to filter CSV data by date range: {e}")
        return csv_data
