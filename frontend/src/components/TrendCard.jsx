/**
 * TrendCard.jsx
 *
 * Shared, purely presentational card component used by Search, GlobalTrends,
 * and IndiaTrends pages. It handles two data shapes:
 *   - ML endpoint data:     { keywords, score, sentiment_label, volume, ... }
 *   - Search endpoint data: { query, trend_score, message }
 *
 * Props:
 *   trend  – trend item object (either shape above)
 *   index  – 0-based position in the list (for rank badge + animation delay)
 */

import React from "react";

/**
 * scoreConfig – maps a numeric trend score to Tailwind colour classes.
 * @param {number} s  Trend score 0–100+
 * @returns {{ text: string, bg: string }}
 */
function scoreConfig(s) {
  if (s >= 70) return { text: "text-emerald-400", bg: "bg-emerald-400/10 border-emerald-400/30" };
  if (s >= 40) return { text: "text-yellow-400",  bg: "bg-yellow-400/10  border-yellow-400/30"  };
  return             { text: "text-slate-400",   bg: "bg-slate-500/10   border-slate-500/20"   };
}

export default function TrendCard({ trend, index }) {
  // Support both ML data shape (keywords/score) and search data shape (query/trend_score)
  const label = trend.keywords ?? trend.query ?? "—";
  const score = trend.score    ?? trend.trend_score ?? 0;
  const pct   = Math.min(score, 100);
  const sc    = scoreConfig(score);

  return (
    <div
      className="group relative rounded-2xl border border-slate-200 dark:border-slate-700/80
        bg-white dark:bg-slate-800/60 p-5 flex flex-col gap-3
        transition-all duration-200 cursor-default overflow-hidden
        hover:-translate-y-1 hover:border-orange-400/40 hover:shadow-glow-sm
        animate-fade-up"
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      {/* Orange accent line revealed on hover */}
      <div className="absolute top-0 left-0 right-0 h-0.5 btn-accent
        opacity-0 group-hover:opacity-100 transition-opacity duration-200" />

      {/* Header row: rank | label | score badge */}
      <div className="flex items-start justify-between gap-3">
        <span className="text-[11px] font-mono font-semibold text-slate-400 dark:text-slate-500
          bg-slate-100 dark:bg-slate-700 border border-slate-200 dark:border-slate-600
          px-2 py-0.5 rounded-md flex-shrink-0">
          #{index + 1}
        </span>

        <p className="flex-1 text-sm font-semibold text-slate-800 dark:text-slate-100 leading-snug">
          {label}
        </p>

        <div className="flex items-center gap-1.5 flex-shrink-0">
          {/* Momentum Indicator */}
          {trend.velocity !== undefined && (
            <span className={`text-xs font-bold ${trend.velocity > 0 ? 'text-emerald-500' : trend.velocity < 0 ? 'text-red-500' : 'text-slate-400'}`}>
              {trend.velocity > 0 ? '▲' : trend.velocity < 0 ? '▼' : '―'}
            </span>
          )}
          <span className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${sc.bg} ${sc.text}`}>
            {score}
          </span>
        </div>
      </div>

      {/* Sentiment label (only shown for ML data) */}
      {trend.sentiment_label && (
        <span className="text-[10px] font-semibold uppercase tracking-widest
          text-slate-400 dark:text-slate-500">
          {trend.sentiment_label === "positive" ? "🟢" :
           trend.sentiment_label === "negative" ? "🔴" : "⚪"} {trend.sentiment_label}
        </span>
      )}

      {/* Progressive Tri-Color Sentiment Bar or Solid Bar */}
      <div className="flex items-center gap-2.5">
        <div className="flex-1 h-1.5 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden flex">
          {trend.positive_pct !== undefined ? (
            <>
              <div className="h-full bg-emerald-400/80 transition-all duration-700" style={{ width: `${Math.round(trend.positive_pct * 100)}%` }} title="Positive" />
              <div className="h-full bg-slate-400/50 transition-all duration-700" style={{ width: `${Math.round(trend.neutral_pct * 100)}%` }} title="Neutral" />
              <div className="h-full bg-red-400/80 transition-all duration-700" style={{ width: `${Math.round(trend.negative_pct * 100)}%` }} title="Negative" />
            </>
          ) : (
            <div className="h-full rounded-full btn-accent transition-all duration-700" style={{ width: `${pct}%` }} />
          )}
        </div>
        <span className="text-[11px] font-mono font-semibold text-slate-400 dark:text-slate-500 min-w-[28px] text-right">
          {pct}
        </span>
      </div>

      {/* Top Post Context Excerpt */}
      {trend.top_posts && (
        <div className="mt-1 border-t border-slate-100 dark:border-slate-700/50 pt-3 flex flex-col gap-1">
          <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1">
            <span className="w-1 h-1 rounded-full bg-orange-400 animate-pulse"></span> Context Header
          </span>
          <p className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed italic">
            "{trend.top_posts.split('|')[0] || trend.top_posts}"
          </p>
        </div>
      )}
    </div>
  );
}
