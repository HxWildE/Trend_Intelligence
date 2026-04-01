/**
 * GlobalTrends.jsx  — Route: "/trends"
 *
 * Page responsibility: fetches trends from the /trends API and composes
 * TrendCard + Graph to display them.
 *
 * Components used:
 *   TrendCard – renders each individual trend item (stateless)
 *   Graph     – renders an SVG bar chart of the trend data (stateless)
 *
 * API calls:
 *   getTrends()  →  GET /trends
 */

import React, { useEffect, useState } from "react";
import { getTrends } from "../services/api";
import TrendCard from "../components/TrendCard";
import Graph from "../components/Graph";
import NewsFeed from "../components/NewsFeed";

/* ── Refresh Icon ───────────────────────────────────────────────── */
const IconRefresh = ({ spinning }) => (
  <svg
    width="14" height="14"
    className={`w-3.5 h-3.5 ${spinning ? "animate-spin" : ""}`}
    viewBox="0 0 24 24" fill="none" stroke="currentColor"
    strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
  >
    <polyline points="23 4 23 10 17 10" />
    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
  </svg>
);

/* ── Category filter chips and heuristics ─────── */
const CATEGORIES = ["All", "Technology", "Sports", "Politics", "Entertainment", "Finance"];

const CATEGORY_KEYWORDS = {
  Technology: ["tech", "ai", "software", "app", "apple", "google", "meta", "microsoft", "cyber", "internet", "data", "robot", "crypto", "bitcoin", "digital", "phone"],
  Sports: ["cricket", "ipl", "football", "match", "tennis", "olympics", "bcci", "fifa", "player", "tournament", "score", "wwe", "ufc", "team"],
  Politics: ["election", "modi", "biden", "trump", "government", "parliament", "congress", "bjp", "policy", "minister", "court", "law", "vote"],
  Entertainment: ["movie", "film", "actor", "actress", "cinema", "music", "song", "hollywood", "bollywood", "netflix", "show", "review", "box office", "singer", "concert"],
  Finance: ["stock", "market", "budget", "economy", "nifty", "sensex", "bank", "hdfc", "sbi", "shares", "trading", "invest", "tax", "rbi"]
};

/* ── Page Component ─────────────────────────────────────────────── */
export default function GlobalTrends() {
  /** trends – array of { query, trend_score } objects from the API */
  const [trends, setTrends] = useState([]);
  /** loading – true during initial fetch and manual refresh */
  const [loading, setLoading] = useState(true);
  /** error – string shown when the API call fails */
  const [error, setError] = useState(null);
  /** spinning – keeps the refresh icon rotating for visual feedback */
  const [spinning, setSpinning] = useState(false);
  /** active – currently selected category chip (UI only) */
  const [active, setActive] = useState("All");
  /** showGraph – toggles the Graph component in/out */
  const [showGraph, setShowGraph] = useState(false);

  /**
   * fetchData – calls the API service, updates trends state.
   * Guards against non-array responses so the grid never crashes.
   */
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getTrends();
      setTrends(Array.isArray(data) ? data : []);
    } catch {
      setError("Could not load trends. Check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  /**
   * handleRefresh – re-fetches data on demand.
   * Keeps the spinner running for at least 650ms for clear visual feedback.
   */
  const handleRefresh = async () => {
    setSpinning(true);
    await fetchData();
    setTimeout(() => setSpinning(false), 650);
  };

  /* Auto-fetch once when the component mounts (user navigates to /trends) */
  useEffect(() => { fetchData(); }, []);

  /** getFilteredTrends – computes the displayed subset of trends based on the active category */
  const getFilteredTrends = () => {
    if (active === "All") return trends;
    const keywords = CATEGORY_KEYWORDS[active] || [];
    return trends.filter(t => {
      const text = (t.keywords || t.query || "").toLowerCase();
      // Match if the trend text contains ANY of the category keywords
      return keywords.some(kw => text.includes(kw));
    });
  };

  const displayedTrends = getFilteredTrends();

  return (
    <>
      {/* ── Page Header ── */}
      <div className="flex items-center justify-between mb-6 animate-fade-up">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl flex items-center justify-center text-sm
            bg-orange-500/15 border border-orange-500/30">
            🌍
          </div>
          <h2 className="text-xl font-black bg-gradient-to-r from-orange-500 to-amber-500 bg-clip-text text-transparent">
            Global Trends
          </h2>
          {!loading && (
            <span className="text-xs text-slate-400 dark:text-slate-500
              bg-slate-100 dark:bg-slate-800 border border-slate-200
              dark:border-slate-700 px-2.5 py-0.5 rounded-full font-medium">
              {displayedTrends.length} topics
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Toggle chart view */}
          {displayedTrends.length > 0 && (
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

          {/* Refresh button */}
          <button
            id="refresh-trends-btn"
            onClick={handleRefresh}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl
              text-sm font-semibold text-white btn-accent shadow-glow-sm
              hover:shadow-glow-md hover:-translate-y-px active:translate-y-0
              transition-all duration-200"
          >
            <IconRefresh spinning={spinning} />
            Refresh
          </button>
        </div>
      </div>

      {/* ── Live News Feed ── */}
      <NewsFeed />

      {/* ── Category Filter Chips ── */}
      <div
        className="flex flex-wrap gap-2 mb-7 animate-fade-up"
        style={{ animationDelay: "0.05s" }}
      >
        {CATEGORIES.map((c) => (
          <button
            key={c}
            onClick={() => setActive(c)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold border
              transition-all duration-200 cursor-pointer
              ${active === c
                ? "text-orange-500 bg-orange-500/10 border-orange-500/30"
                : "text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600"}`}
          >
            {c}
          </button>
        ))}
      </div>

      {/* ── Skeleton ── */}
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
            Failed to load
          </h3>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* ── Empty ── */}
      {!loading && !error && displayedTrends.length === 0 && (
        <div className="text-center py-16 text-slate-400">
          <div className="text-5xl mb-4 animate-float">📭</div>
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-2">
            No trends found for this category
          </h3>
          <p className="text-sm">Try choosing a different category or hit refresh.</p>
        </div>
      )}

      {/* ── Data Views ── */}
      {!loading && !error && displayedTrends.length > 0 && (
        <>
          {/* Spotlight — always shows top trend */}
          <div className="rounded-2xl border border-orange-500/30 bg-orange-500/5
            dark:bg-orange-500/[0.07] p-6 mb-6 animate-fade-up
            transition-all duration-300 hover:shadow-glow-sm">
            <span className="text-[11px] font-bold tracking-widest uppercase text-orange-500">
              🔥 Top Trending
            </span>
            <p className="text-2xl font-extrabold text-slate-900 dark:text-slate-100
              mt-2 mb-4 tracking-tight">
              {displayedTrends[0].keywords ?? displayedTrends[0].query ?? "—"}
            </p>
            <div className="flex items-center gap-3">
              <div className="flex-1 h-2.5 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden flex">
                {displayedTrends[0].positive_pct !== undefined ? (
                  <>
                    <div className="h-full bg-emerald-400/80 transition-all duration-700" style={{ width: `${Math.round(displayedTrends[0].positive_pct * 100)}%` }} title="Positive" />
                    <div className="h-full bg-slate-400/50 transition-all duration-700" style={{ width: `${Math.round(displayedTrends[0].neutral_pct * 100)}%` }} title="Neutral" />
                    <div className="h-full bg-red-400/80 transition-all duration-700" style={{ width: `${Math.round(displayedTrends[0].negative_pct * 100)}%` }} title="Negative" />
                  </>
                ) : (
                  <div className="h-full rounded-full btn-accent transition-all duration-700" style={{ width: `${Math.min(displayedTrends[0].score ?? displayedTrends[0].trend_score ?? 0, 100)}%` }} />
                )}
              </div>
              <span className="text-sm font-bold font-mono text-slate-600 dark:text-slate-300">
                {displayedTrends[0].score ?? displayedTrends[0].trend_score ?? 0}
              </span>
            </div>
          </div>

          {/*
            Conditional view toggle:
            - showGraph = true  → Graph component (pure SVG chart, no API)
            - showGraph = false → TrendCard grid (shared TrendCard component)
          */}
          {showGraph ? (
            <Graph data={displayedTrends} title={`${active} Trends Overview`} limit={12} />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {displayedTrends.map((t, i) => (
                <TrendCard key={i} trend={t} index={i} />
              ))}
            </div>
          )}
        </>
      )}
    </>
  );
}