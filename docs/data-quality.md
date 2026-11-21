# Data quality requirements

1. Public 13F is a **quarter-end snapshot** of reportable long positions, not a trade log or a complete picture of every fund exposure.
2. Record both `report_period` (what the holdings refer to) and `filed_at` (when the public learned them). Historical analysis must use availability on the filing date, not quarter-end.
3. Treat amendments (13F-HR/A) carefully; don't double-count an original and its correction.
4. A fund's average tax/accounting cost basis is not a field in 13F. Cost estimates are hypothetical and can be very uncertain if the manager buys and sells within the same quarter.
5. Use CIK for manager identity, CUSIP/security mapping for filings, and caution when matching to current ticker symbols. Handle splits and corporate actions explicitly.
6. Keep raw SEC documents and original source links for auditable evidence. Follow SEC automated access limits and a descriptive User-Agent.
7. Get appropriate rights to any commercial market-price data, including redistribution rights where applicable.
8. Display confidence and assumptions beside estimates. Never label model outputs as exact transaction prices or verified investor returns.
9. Do not imply a particular fund manager personally made every decision. Filer portfolios are not identical to an individual's full holdings.
