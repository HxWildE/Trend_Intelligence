/**
 * IndiaTrends.jsx  — Route: "/region"
 *
 * Page responsibility: manages selected state, calls the /region API, and
 * composes StateDropdown + TrendCard + Graph to display region-specific trends.
 *
 * Components used:
 *   StateDropdown – renders the state/UT picker (stateless, no API calls)
 *   TrendCard     – renders each trend result card (stateless)
 *   Graph         – renders an SVG bar chart of region trends (stateless)
 *
 * API calls:
 *   getRegionTrends(state)  →  GET /region?state=<stateName>
 */

import React, { useState } from "react";
import { getRegionTrends } from "../services/api";
import StateDropdown, { getFlag } from "../components/StateDropdown";
import TrendCard                  from "../components/TrendCard";
import Graph                      from "../components/Graph";
import NewsFeed                   from "../components/NewsFeed";

/* ── Quick-pick shortcut states ─────────────────────────────────── */
const QUICK = ["Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", "Uttar Pradesh", "Gujarat"];

/* ── Page Component ─────────────────────────────────────────────── */
export default function IndiaTrends() {
  /** state – name of the selected Indian state/UT (drives the API call) */
  const [state, setState]     = useState("India");
  /** data – array of { query, trend_score } returned by the API */
  const [data, setData]       = useState([]);
  /** loading – true while the API call is in-flight */
  const [loading, setLoading] = useState(false);
  /** error – string shown when API call fails */
  const [error, setError]     = useState(null);
  /**
   * fetched – becomes true after the first API call.
   * Distinguishes "never searched" (show prompt) from "searched but empty"
   * (show "no data" message) without relying on data.length alone.
   */
  const [fetched, setFetched] = useState(false);
  /** showGraph – toggles between card grid and SVG chart view */
  const [showGraph, setShowGraph] = useState(false);

  /**
   * handleFetch – validates selection, then calls the service layer.
   *
   * @param {string} [overrideState] – passed by quick-pick chips so they
   *   can fetch immediately without waiting for React to apply setState
   *   (setState is async; calling handleFetch() right after setState(s)
   *   would still read the old state value).
   */
  const handleFetch = async (overrideState) => {
    const target = overrideState ?? state;

    setLoading(true);
    setError(null);
    setData([]);

    try {
      const res = await getRegionTrends(target);
      setData(Array.isArray(res) ? res : []);
    } catch {
      setError("Could not load region trends. Check backend.");
    } finally {
      setLoading(false);
      setFetched(true);
    }
  };

  return (
    <>
      {/* ── Page Header ── */}
      <div className="flex items-center justify-between mb-3 animate-fade-up">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl flex items-center justify-center text-sm
            bg-orange-500/15 border border-orange-500/30">
            🗺️
          </div>
          <h2 className="text-xl font-black bg-gradient-to-r from-orange-500 to-amber-500 bg-clip-text text-transparent">
            India Region Trends
          </h2>
          {fetched && !loading && (
            <span className="text-xs text-slate-400 dark:text-slate-500
              bg-slate-100 dark:bg-slate-800 border border-slate-200
              dark:border-slate-700 px-2.5 py-0.5 rounded-full font-medium">
              {data.length} results · {state === "India" ? "All India" : state}
            </span>
          )}
        </div>

        {/* Chart toggle — only shown after data is loaded */}
        {data.length > 0 && (
          <button
            onClick={() => setShowGraph((v) => !v)}
            className="px-3.5 py-2 rounded-xl text-sm font-semibold border
              transition-all duration-200
              text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800
              border-slate-200 dark:border-slate-700
              hover:text-orange-500 hover:border-orange-300 dark:hover:border-orange-500/40"
          >
            {showGraph ? "📋 Cards" : "📊 Chart"}
          </button>
        )}
      </div>

      <p
        className="text-sm text-slate-400 dark:text-slate-500 mb-6 animate-fade-up"
        style={{ animationDelay: "0.05s" }}
      >
        Select any state or union territory to see what people are searching right now.
      </p>

      {/* ── Controls Row ── */}
      <div
        className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mb-5 animate-fade-up"
        style={{ animationDelay: "0.08s" }}
      >
        {/* Live state preview pill — updates as user changes dropdown */}
        <div className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl
          bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700
          flex-shrink-0 min-w-[140px]">
          <span className="text-2xl leading-none">
            {state === "India" ? "🇮🇳" : getFlag(state)}
          </span>
          <span className="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">
            {state === "India" ? "All India" : state}
          </span>
        </div>

        {/*
          StateDropdown is fully controlled:
            - value    → displays whatever `state` is currently set to
            - onChange → updates `state` in this page (no API call yet)
          The API call only happens when the user clicks "Get Trends".
        */}
        <StateDropdown value={state} onChange={setState} />

        {/* "Get Trends" button — triggers handleFetch() with current state */}
        <button
          id="fetch-region-btn"
          onClick={() => handleFetch()}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl
            text-sm font-bold text-white btn-accent shadow-glow-sm
            hover:shadow-glow-md hover:-translate-y-px active:translate-y-0
            transition-all duration-200 flex-shrink-0
            disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {loading ? "⏳ Loading…" : "🔍 Get Trends"}
        </button>
      </div>

      {/* ── Quick-pick Chips ── */}
      <div
        className="flex flex-wrap gap-2 mb-8 animate-fade-up"
        style={{ animationDelay: "0.1s" }}
      >
        {QUICK.map((s) => (
          <button
            key={s}
            onClick={() => {
              setState(s);            // update the dropdown display
              handleFetch(s);         // fetch immediately with the override
            }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full
              text-xs font-semibold border transition-all duration-200 cursor-pointer
              ${state === s
                ? "text-orange-500 bg-orange-500/10 border-orange-500/30"
                : "text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600"}`}
          >
            <span>{getFlag(s)}</span>
            {s}
          </button>
        ))}
      </div>

      {/* ── Live State News Feed ── */}
      <NewsFeed region={state} />

      {/* ── Loading Skeleton ── */}
      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton rounded-2xl h-32"
              style={{ animationDelay: `${i * 0.08}s` }} />
          ))}
        </div>
      )}

      {/* ── Error ── */}
      {error && !loading && (
        <div className="text-center py-16 text-slate-400">
          <div className="text-5xl mb-4 animate-float">⚠️</div>
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-2">
            Something went wrong
          </h3>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* ── Initial Prompt (never fetched yet) ── */}
      {!fetched && !loading && (
        <div className="text-center py-16 text-slate-400">
          <div className="text-6xl mb-5 animate-float">🗺️</div>
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-2">
            Choose a state and hit "Get Trends"
          </h3>
          <p className="text-sm">Discover what's trending across 36 states &amp; UTs of India.</p>
        </div>
      )}

      {/* ── Empty Result (fetched but API returned nothing) ── */}
      {fetched && !loading && !error && data.length === 0 && (
        <div className="text-center py-16 text-slate-400">
          <div className="text-6xl mb-5 animate-float">{getFlag(state)}</div>
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-2">
            No data for {state}
          </h3>
          <p className="text-sm">Try another state or check the backend response.</p>
        </div>
      )}

      {/* ── Results ── */}
      {!loading && !error && data.length > 0 && (
        <>
          {/* Spotlight — top result for this region */}
          <div className="rounded-2xl border border-orange-500/30 bg-orange-500/5
            dark:bg-orange-500/[0.07] p-6 mb-6 animate-fade-up
            transition-all duration-300 hover:shadow-glow-sm">
            <div className="flex items-center gap-2.5 mb-2">
              <span className="text-2xl">
                {state === "India" ? "🇮🇳" : getFlag(state)}
              </span>
              <span className="text-[11px] font-bold tracking-widest uppercase text-orange-500">
                Top Trend · {state === "India" ? "All India" : state}
              </span>
            </div>
            <p className="text-2xl font-extrabold text-slate-900 dark:text-slate-100
              mb-4 tracking-tight">
              {data[0].keywords ?? data[0].query ?? "—"}
            </p>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-2.5 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
                <div
                  className="h-full rounded-full btn-accent transition-all duration-700"
                  style={{ width: `${Math.min(data[0].score ?? data[0].trend_score ?? 0, 100)}%` }}
                />
              </div>
              <span className="text-sm font-bold font-mono text-slate-600 dark:text-slate-300">
                {data[0].score ?? data[0].trend_score ?? 0}
              </span>
            </div>
          </div>

          {/*
            Conditional view toggle:
            - showGraph = true  → Graph (pure chart, receives data as prop)
            - showGraph = false → TrendCard grid (shared component)
          */}
          {showGraph ? (
            <Graph
              data={data}
              title={`${state === "India" ? "All India" : state} — Trend Chart`}
              limit={12}
            />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {data.map((item, i) => (
                <TrendCard key={i} trend={item} index={i} />
              ))}
            </div>
          )}
        </>
      )}
    </>
  );
}