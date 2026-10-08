import pandas as pd
import pytest


@pytest.fixture
def sample_anime_data() -> pd.DataFrame:
    return pd.DataFrame({
        "MAL_ID": [1, 2, 3, 4, 5],
        "Name": ["A", "B", "C", "D", "E"],
        "Completed": [100, 80, 60, 40, 20],
        "Members": [200, 160, 120, 80, 40],
    })
