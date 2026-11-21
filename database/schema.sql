-- Proposed PostgreSQL schema for future REAL data, not used by the demo.
-- Designed for official SEC filings and provenance; not a complete 13F parser.
CREATE TABLE managers (
  id BIGSERIAL PRIMARY KEY,
  sec_cik VARCHAR(10) UNIQUE NOT NULL,
  legal_name TEXT NOT NULL,
  display_name TEXT
);

CREATE TABLE filings (
  id BIGSERIAL PRIMARY KEY,
  manager_id BIGINT NOT NULL REFERENCES managers(id),
  accession_number TEXT NOT NULL UNIQUE,
  report_period DATE NOT NULL,
  filed_at TIMESTAMPTZ NOT NULL,
  form_type TEXT NOT NULL,
  source_url TEXT NOT NULL,
  is_amendment BOOLEAN NOT NULL DEFAULT FALSE,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX filings_manager_period_idx ON filings(manager_id, report_period DESC);

CREATE TABLE securities (
  id BIGSERIAL PRIMARY KEY,
  cusip VARCHAR(9),
  ticker TEXT,
  issuer_name TEXT NOT NULL,
  share_class TEXT,
  UNIQUE (cusip, issuer_name, share_class)
);
CREATE INDEX securities_ticker_idx ON securities(ticker);

CREATE TABLE positions (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
  security_id BIGINT NOT NULL REFERENCES securities(id),
  shares NUMERIC(24,4),
  reported_value_usd NUMERIC(24,2),
  put_call TEXT,
  discretion TEXT,
  source_row_index INTEGER,
  UNIQUE (filing_id, source_row_index)
);
CREATE INDEX positions_filing_idx ON positions(filing_id);

CREATE TABLE adjusted_prices (
  security_id BIGINT NOT NULL REFERENCES securities(id),
  price_date DATE NOT NULL,
  adjusted_close NUMERIC(20,6) NOT NULL,
  price_provider TEXT NOT NULL,
  PRIMARY KEY (security_id, price_date, price_provider)
);

CREATE TABLE cost_estimates (
  id BIGSERIAL PRIMARY KEY,
  filing_id BIGINT NOT NULL REFERENCES filings(id),
  security_id BIGINT NOT NULL REFERENCES securities(id),
  model_version TEXT NOT NULL,
  estimated_low NUMERIC(20,4),
  estimated_high NUMERIC(20,4),
  confidence TEXT CHECK (confidence IN ('high','medium','low','insufficient')),
  assumptions JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (filing_id, security_id, model_version)
);
-- Before production: implement amendment resolution, share classes, CUSIP mappings,
-- option handling, provider licenses, row-level security, access roles, and audit logging.
