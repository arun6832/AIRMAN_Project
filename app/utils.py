def safe_float(x, default=None):
    try:
        return float(x)
    except Exception:
        return default
