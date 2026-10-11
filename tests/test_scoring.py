import pandas as pd
import numpy as np
from analysis.scoring import score_symbol

def test_targets_and_stop_are_valid():
    n = 180
    idx = pd.date_range("2025-01-01", periods=n, freq="B")
    close = np.linspace(100, 150, n)
    df = pd.DataFrame({
        "Open": close * .995, "High": close * 1.01,
        "Low": close * .99, "Close": close,
        "Volume": np.full(n, 100000),
    }, index=idx)
    result = score_symbol("TEST.NS", df, {"score": None, "article_count": 0, "label": "UNAVAILABLE"})
    assert result["entry"] > 0
    assert result["stop_loss"] < result["entry"]
    assert len(result["targets"]) == 4
    assert result["targets"][0] == result["entry"] * 1.07
    assert result["targets"][3] == result["entry"] * 1.28
    assert 0 <= result["score"] <= 100
