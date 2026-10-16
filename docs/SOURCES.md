# Source, provenance and licensing

- [Superstore Sales Dataset on Kaggle](https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting), uploader Rohit Sahoo. The data card describes a four-year retail sample and labels its license **GPL 2**, with update frequency Never.
- Download endpoint: https://www.kaggle.com/api/v1/datasets/download/rohitsahoo/sales-forecasting
- Downloaded October 15, 2026. Original file `train.csv`, 9,800 lines, 18 columns. SHA-256: `dbb0f167b27ccf02d7ff8cb0446a9abc6dbc3522e83cf9daa6939801acfdd196`.
- Original Order Date range: January 3, 2015–December 30, 2018, parsed as day/month/year.
- This project selects eight original fields and splits by received order month. No sales records are fabricated, extended or relabeled as current activity. The source itself is a Superstore sample; no real client or retailer engagement is claimed.
- The mirror does not define a currency. Monetary values are retained in source units; no dollar label or exchange rate is invented.
- Customer Name, Customer ID, address-related fields and other unused columns are omitted from the included selected-column deliveries.

Original project code and documentation are MIT licensed, see root LICENSE. The source dataset and data-derived reports retain the Kaggle GPL 2 label; its license text is in data/LICENSE. The transformation and source fingerprint are documented in source-provenance.json. Upstream licensing and provenance are described as the mirror presents them; no authorship of the source dataset is claimed.
