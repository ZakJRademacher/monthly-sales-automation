"""Download the historical Kaggle Superstore sales snapshot."""

import shutil
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / "data/raw"
target.mkdir(parents=True, exist_ok=True)
archive = target / "kaggle-sales.zip"
urllib.request.urlretrieve(
    "https://www.kaggle.com/api/v1/datasets/download/rohitsahoo/sales-forecasting",
    archive,
)
with zipfile.ZipFile(archive) as z:
    name = next(n for n in z.namelist() if Path(n).name.lower() == "train.csv")
    with z.open(name) as source, (target / "train.csv").open("wb") as output:
        shutil.copyfileobj(source, output)
print(target / "train.csv")
