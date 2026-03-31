/**
 * Search.jsx  — Route: "/"
 *
 * Page responsibility: owns search state, calls the /search API through the
 * service layer, and composes SearchBar + TrendCard to build the UI.
 *
 * Components used:
 *   SearchBar  – renders the input box + button (stateless)
 *   TrendCard  – renders the score result card (stateless)
 *
 * API calls:
 *   searchQuery(term)  →  GET /search?q=<term>
 */

import React, { useState } from "react";
import { searchQuery } from "../services/api";
import SearchBar from "../components/SearchBar";
import TrendCard from "../components/TrendCard";

/* ── Quick-search shortcuts ─────────────────────────────────────── */
const HOT_TOPICS = [
  "IPL 2026", "Budget 2026", "AI Tools", "Stock Market",
  "Jio Plans", "Movie Reviews", "Cricket Live", "UPSC 2026",
];

/* ── Score label helper ─────────────────────────────────────────── */
/**
 * scoreLabel – returns a human-readable label for a trend score.
 * Used in the result card description text.
 * @param {number} s
 * @returns {string}
 */
function scoreLabel(s) {
  if (s >= 70) return "Trending massively right now";
  if (s >= 40) return "Moderate search interest";
  return "Low search volume currently";
}

/* ── Page Component ─────────────────────────────────────────────── */
export default function Search() {
  /** query – the current text in the search box (lifted up from SearchBar) */
  const [query, setQuery] = useState("");
  /** result – the API response object: { query, trend_score } */
  const [result, setResult] = useState(null);
  /** loading – true while the API call is in-flight */
  const [loading, setLoading] = useState(false);
  /** error – string message shown when the API call fails */
  const [error, setError] = useState(null);

  /**
   * doSearch – validates the query then calls the service layer.
   * Clears previous result/error before each new request.
   * @param {string} [term] – optional override (used by hot-topic chips)
   */
  const doSearch = async (term) => {
    const keyword = term ?? query;
    if (!keyword?.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await searchQuery(keyword);
      setResult(data);
      setQuery(keyword);   // reflect what was actually searched
    } catch {
      setError("Could not reach the API. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* ── Hero Banner ── */}
      <section className="relative rounded-2xl overflow-hidden mb-10 min-h-[260px]
        flex items-end animate-fade-up">
        <img
          src="/hero_banner.png"
          alt="Trend Intelligence hero"
          className="absolute inset-0 w-full h-full object-cover object-center"
        />
        <div
          className="absolute inset-0"
          style={{ background: "linear-gradient(to top, rgba(13,17,23,0.97) 0%, rgba(13,17,23,0.55) 55%, transparent 100%)" }}
        />
        <div className="relative z-10 p-8 sm:p-10 w-full">
          <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold
            tracking-widest uppercase text-orange-400 bg-orange-500/15
            border border-orange-500/30 px-3 py-1 rounded-full mb-4">
            📡 Real-Time Intelligence
          </span>
          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight
            leading-tight mb-3 gradient-text">
            Discover What India<br />Is Searching Right Now
          </h1>
          <p className="text-slate-400 text-sm sm:text-base max-w-xl mb-5">
            Live trend scores, regional breakdowns and intelligent search — all in one place.
          </p>
          <div className="flex gap-6">
            {[["36", "States & UTs"], ["Live", "Data Feed"], ["0–100", "Trend Score"]].map(([v, l]) => (
              <div key={l} className="flex flex-col">
                <span className="text-xl font-bold text-white">{v}</span>
                <span className="text-xs text-slate-400">{l}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Search Section ── */}
      <div className="text-center mb-6 animate-fade-up" style={{ animationDelay: "0.05s" }}>
        <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-2
          text-slate-900 dark:text-slate-100">
          Search Any Trend
        </h2>
        <p className="text-slate-400 dark:text-slate-500 text-sm mb-7">
          Type a keyword and get its live intelligence score
        </p>

        {/*
          SearchBar is controlled:
            - value / onChange → SearchBar displays and updates `query` state here in Search.jsx
            - onSearch        → SearchBar calls doSearch() when button is clicked or Enter pressed
            - loading         → SearchBar disables the button and shows "Searching…"
        */}
        <SearchBar
          value={query}
          onChange={setQuery}
          onSearch={() => doSearch()}
          loading={loading}
        />
      </div>

      {/* ── Hot Topic Chips ── */}
      <div
        className="flex flex-wrap justify-center gap-2 mb-10 animate-fade-up"
        style={{ animationDelay: "0.1s" }}
      >
        {HOT_TOPICS.map((t) => (
          <button
            key={t}
            onClick={() => doSearch(t)}
            className="px-3 py-1.5 rounded-full text-xs font-semibold border
              transition-all duration-200 cursor-pointer
              text-orange-500 bg-orange-500/10 border-orange-500/25
              hover:bg-orange-500/20 hover:border-orange-500/50 hover:-translate-y-px"
          >
            🔥 {t}
          </button>
        ))}
      </div>

      {/* ── Loading Skeleton ── */}
      {loading && (
        <div className="max-w-md mx-auto rounded-2xl border border-slate-200
          dark:border-slate-700 p-5 bg-white dark:bg-slate-800/70">
          <div className="skeleton h-3 w-1/3 rounded mb-4" />
          <div className="skeleton h-5 w-2/3 rounded mb-5" />
          <div className="skeleton h-2 w-full rounded-full" />
        </div>
      )}

      {/* ── Error Banner ── */}
      {error && !loading && (
        <div className="max-w-md mx-auto rounded-2xl border border-orange-500/30
          bg-orange-500/5 p-5 animate-fade-in">
          <p className="text-orange-400 text-sm font-medium">⚠️ {error}</p>
        </div>
      )}

      {/*
        Result Card — uses the shared TrendCard component.
        We wrap it in a centred div so it stays max-width on desktop.
        TrendCard receives: trend object + index=0 (it's the only result).
      */}
      {result && !loading && (
        <div className="max-w-md mx-auto animate-fade-up">
          {/* Score label sits above the card */}
          <p className="text-xs text-slate-400 dark:text-slate-500 text-center mb-2 font-medium">
            {scoreLabel(result.trend_score)}
          </p>
          <TrendCard trend={result} index={0} />
        </div>
      )}
    </>
  );
}