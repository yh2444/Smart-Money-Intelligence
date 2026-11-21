"use client";

import { useMemo, useState } from "react";
import demo from "@/data/sample.json";

type Position = (typeof demo.managers)[number]["holdings"][number];
type DisplayPosition = Position & { managerName: string; managerId: string };
const allPositions: DisplayPosition[] = demo.managers.flatMap((manager) => manager.holdings.map((holding) => ({ ...holding, managerName: manager.name, managerId: manager.id })));
const usd = (value: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
const signed = (value: number) => `${value > 0 ? "+" : ""}${value.toFixed(1)}%`;

export default function Home() {
  const [query, setQuery] = useState("");
  const [manager, setManager] = useState("all");
  const [sort, setSort] = useState("weight");
  const [watchlist, setWatchlist] = useState<string[]>([]);

  const records = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return allPositions
      .filter((p) => (manager === "all" || p.managerId === manager) && (!normalized || [p.ticker, p.company, p.managerName].some((x) => x.toLowerCase().includes(normalized))))
      .sort((a, b) => sort === "change" ? b.change - a.change : sort === "ticker" ? a.ticker.localeCompare(b.ticker) : b.weight - a.weight);
  }, [query, manager, sort]);

  const countTickers = new Set(allPositions.map((p) => p.ticker)).size;
  const isWatching = (ticker: string) => watchlist.includes(ticker);
  const toggleWatch = (ticker: string) => setWatchlist((old) => old.includes(ticker) ? old.filter((t) => t !== ticker) : [...old, ticker]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a href="#overview" className="brand"><span className="brand-mark">S</span><span>SMART MONEY <small>INTELLIGENCE</small></span></a>
        <p className="nav-label">WORKSPACE</p>
        <nav className="side-nav" aria-label="Main navigation">
          <a href="#overview" className="selected"><span>◈</span> Overview</a>
          <a href="#managers"><span>♧</span> Investor explorer</a>
          <a href="#holdings"><span>▥</span> Holdings analyzer</a>
          <a href="#method"><span>◎</span> Method & evidence</a>
        </nav>
        <div className="sidebar-bottom"><div className="live-dot" /> <span>Prototype environment</span><p>Built for public-filing research.<br/>Not investment advice.</p></div>
      </aside>

      <main className="main" id="overview">
        <div className="topbar"><div className="breadcrumb">Workspace <span>/</span> Dashboard</div><div className="topbar-right"><span className="demo-pill">● SYNTHETIC DATA</span><span className="avatar">SM</span></div></div>
        <div className="content">
          <section className="hero">
            <div className="eyebrow">INVESTMENT RESEARCH · PROTOTYPE</div>
            <h1>Understand the moves<br/><em>behind the money.</em></h1>
            <p>Explore institutional positions, compare holdings, and inspect estimated cost ranges — with transparent assumptions and source tracking.</p>
            <div className="hero-actions"><a className="primary-button" href="#holdings">Explore holdings <span>↗</span></a><a className="text-button" href="https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets" target="_blank" rel="noopener noreferrer">Explore SEC data ↗</a></div>
          </section>
          <div className="warning" role="status"><span className="warning-icon">!</span><div><strong>Demo mode — all displayed prices, positions and managers are fictional.</strong><span>No real SEC filings or live prices have been imported. Replace the sample dataset before using the product for actual research.</span></div></div>
          <section className="metrics" aria-label="Prototype metrics">
            <article className="metric"><span>Demo managers</span><strong>{demo.managers.length}</strong><small>fictional examples</small></article>
            <article className="metric"><span>Unique tickers</span><strong>{countTickers}</strong><small>in local sample data</small></article>
            <article className="metric"><span>Sample holdings</span><strong>{allPositions.length}</strong><small>synthetic position records</small></article>
            <article className="metric"><span>Verified SEC filings</span><strong>0</strong><small>ingestion not connected</small></article>
          </section>

          <section className="section" id="managers">
            <div className="section-heading"><div><span className="eyebrow muted">DISCOVER</span><h2>Investor explorer</h2><p>Choose a manager to filter the holdings table.</p></div><span className="section-tag">3 sample profiles</span></div>
            <div className="manager-grid">
              {demo.managers.map((m) => <button className={`manager-card ${manager === m.id ? "active" : ""}`} type="button" key={m.id} onClick={() => { setManager(manager === m.id ? "all" : m.id); document.getElementById("holdings")?.scrollIntoView({ behavior: "smooth", block: "start" }); }}>
                <div className="manager-top"><span className="manager-avatar">{m.initials}</span><span className="manager-arrow">↗</span></div>
                <strong>{m.name}</strong><span className="manager-style">{m.style}</span><span className="manager-count">{m.holdings.length} demo positions · fictional</span>
              </button>)}
            </div>
          </section>

          <section className="section" id="holdings">
            <div className="section-heading"><div><span className="eyebrow muted">ANALYZE</span><h2>Holdings intelligence</h2><p>Search by ticker, company name, or manager. Cost ranges are illustrative only.</p></div><span className="section-tag">Example quarter</span></div>
            <div className="holdings-panel">
              <div className="toolbar">
                <label className="search" htmlFor="stock-search"><span aria-hidden>⌕</span><input id="stock-search" placeholder="Search NVDA, Microsoft, fund..." value={query} onChange={(e) => setQuery(e.target.value)}/>{query && <button aria-label="Clear search" className="clear-button" type="button" onClick={() => setQuery("")}>×</button>}</label>
                <label className="select-wrap"><span className="sr-only">Manager</span><select value={manager} onChange={(e) => setManager(e.target.value)}><option value="all">All managers</option>{demo.managers.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}</select></label>
                <label className="select-wrap"><span className="sr-only">Sort by</span><select value={sort} onChange={(e) => setSort(e.target.value)}><option value="weight">Sort: Weight</option><option value="change">Sort: Change</option><option value="ticker">Sort: Ticker</option></select></label>
              </div>
              <div className="table-scroll"><table className="holdings-table"><thead><tr><th>STOCK / COMPANY</th><th>MANAGER</th><th>PORTFOLIO WT.</th><th>QUARTER CHANGE</th><th>EST. COST RANGE</th><th>DEMO PRICE</th><th>CONFIDENCE</th><th>TRACK</th></tr></thead><tbody>{records.map((p) => <tr key={`${p.managerId}-${p.ticker}`}><td><div className="ticker"><strong>{p.ticker}</strong><span>{p.company}</span></div></td><td><span className="manager-cell">{p.managerName}</span></td><td>{p.weight.toFixed(1)}%</td><td><span className={`change ${p.change >= 0 ? "positive" : "negative"}`}>{signed(p.change)}</span></td><td><span className="cost">{usd(p.costLow)}–{usd(p.costHigh)}</span></td><td>{usd(p.marketPrice)}</td><td><span className="confidence">{p.confidence}</span></td><td><button type="button" className={`watch-button ${isWatching(p.ticker) ? "watching" : ""}`} aria-label={`${isWatching(p.ticker) ? "Remove" : "Add"} ${p.ticker} ${isWatching(p.ticker) ? "from" : "to"} watchlist`} aria-pressed={isWatching(p.ticker)} onClick={() => toggleWatch(p.ticker)}>{isWatching(p.ticker) ? "★" : "☆"}</button></td></tr>)}</tbody></table></div>
              {!records.length && <div className="empty">No matching sample holdings. Try another ticker or choose “All managers.”</div>}
              <div className="table-footer"><span>Showing {records.length} of {allPositions.length} synthetic records</span><span>{watchlist.length} tickers selected for this session · not saved</span></div>
            </div>
          </section>
          <section className="section" id="method"><div className="section-heading"><div><span className="eyebrow muted">TRANSPARENCY</span><h2>How to make this real</h2><p>A trustworthy research platform should show exactly what is known and what is estimated.</p></div></div><div className="method-grid"><article className="method-card"><span className="method-number">01</span><h3>Official 13F filings</h3><p>Import original filings, accession numbers, filing dates and reporting periods from SEC EDGAR.</p></article><article className="method-card"><span className="method-number">02</span><h3>Position changes</h3><p>Compare quarter-end snapshots. A change is not the same as knowing each trade or execution price.</p></article><article className="method-card"><span className="method-number">03</span><h3>Cost estimates</h3><p>Calculate ranges with price history and explicit assumptions, never pretend the estimates are real reported cost bases.</p></article></div></section>
          <footer>SMART MONEY INTELLIGENCE / PROTOTYPE <span>Sample data only · No investment advice · Not affiliated with SEC</span></footer>
        </div>
      </main>
    </div>
  );
}
