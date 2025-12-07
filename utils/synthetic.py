from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd


def _seasonality_term(n: int, period: int = 52) -> np.ndarray:
    weeks = np.arange(n)
    return 0.5 * np.sin(2 * np.pi * weeks / period)


def generate_media_marketing_data(
    num_rows: int,
    channels: List[str],
    include_seasonality: bool = True,
    include_price: bool = True,
    noise_scale: float = 0.5,
    random_seed: int = 123,
) -> pd.DataFrame:
    """Generate synthetic media/marketing data with confounding.

    Variables:
    - Media channels (treatments): e.g., tv, search, social, display, email
    - Outcome: sales
    - Confounders: seasonality, price (affect both spend and sales)
    """
    assert num_rows > 0
    rng = np.random.default_rng(random_seed)

    # Base latent demand driver
    base = rng.normal(loc=10.0, scale=1.0, size=num_rows)

    seasonality = _seasonality_term(num_rows) if include_seasonality else np.zeros(num_rows)
    price = rng.normal(loc=100.0, scale=5.0, size=num_rows) if include_price else np.zeros(num_rows)

    # Channel spend determined by base demand + seasonality + noise (and slightly by price)
    data: Dict[str, np.ndarray] = {}
    for ch in channels:
        noise = rng.normal(scale=1.0, size=num_rows)
        data[ch] = (
            2.0 * base
            + 3.0 * seasonality
            - 0.03 * price
            + noise
        )
        # Ensure non-negative spend
        data[ch] = np.clip(data[ch] - data[ch].min() + 1.0, 0, None)

    # Diminishing returns: log transform channel effects
    channel_effect = sum(0.8 * np.log1p(data[ch]) for ch in channels)

    # Outcome depends on channels + confounders + noise
    outcome = (
        5.0
        + 1.5 * channel_effect
        + 2.5 * seasonality
        - 0.05 * price
        + rng.normal(scale=noise_scale, size=num_rows)
    )

    df = pd.DataFrame({ch: data[ch] for ch in channels})
    if include_seasonality:
        df["seasonality"] = seasonality
    if include_price:
        df["price"] = price
    df["sales"] = outcome
    return df
