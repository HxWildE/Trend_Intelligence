/**
 * Graph.jsx
 *
 * Pure visualization component — receives an array of trend data and renders
 * it as an SVG horizontal bar chart. Contains NO API calls and NO state.
 * The parent page is responsible for fetching data and passing it in.
 *
 * Props:
 *   data  – Array<{ query: string, trend_score: number }>
 *   title – string  – optional chart heading (default: "Trend Chart")
 *   limit – number  – max items to show (default: 10)
 */

import React from "react";

/** Maps score → bar colour class */
function barColor(score) {
  if (score >= 70) return "#34d399"; // emerald-400
  if (score >= 40) return "#fbbf24"; // yellow-400
  return "#94a3b8";                  // slate-400
}

export default function Graph({ data = [], title = "Trend Chart", limit = 10 }) {
  if (!data || data.length === 0) return null;

  const items = data.slice(0, limit);

  // Normalise field names: ML data uses `score` + `keywords`, search data uses `trend_score` + `query`
  const normalised = items.map((d) => {
    let rawLabel = d.keywords ?? d.query ?? "—";
    
    // Parse out messy comma-separated tuples (.si, aivideos, etc) into clean short titles
    if (rawLabel.includes(",")) {
      const parts = rawLabel.split(',').map(s => s.trim().replace(/^[^a-z0-9]+/i, '')).filter(Boolean);
      rawLabel = parts.slice(0, 2).join(', ');
    }

    return {
      label: rawLabel,
      score: d.score ?? d.trend_score ?? 0,
    };
  });

  const maxScore = Math.max(...normalised.map((d) => d.score), 1);

  /* SVG layout constants */
  const ROW_H = 40;   // height per bar row
  const LABEL_W = 160;  // left column width for query labels
  const BAR_AREA = 220;  // width of the bar + score area
  const PAD = 16;   // top/bottom padding
  const SVG_W = LABEL_W + BAR_AREA + 8;
  const SVG_H = normalised.length * ROW_H + PAD * 2;

  return (
    <div className="rounded-3xl border border-slate-200/60 dark:border-slate-700/50
      bg-white/60 dark:bg-slate-800/40 backdrop-blur-lg shadow-xl shadow-slate-200/20 dark:shadow-none p-8 animate-fade-up">

      {/* Title */}
      <div className="flex items-center gap-2 mb-4">
        <div className="w-7 h-7 rounded-lg bg-orange-500/15 border border-orange-500/30
          flex items-center justify-center text-sm">
          📊
        </div>
        <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100">{title}</h3>
        <span className="ml-auto text-xs text-slate-400 dark:text-slate-500 font-medium">
          Top {items.length}
        </span>
      </div>

      {/* SVG Container to prevent massive zooming on wide screens */}
      <div className="w-full max-w-2xl mx-auto pt-4">
        <svg
          width="100%"
          viewBox={`0 0 ${SVG_W} ${SVG_H}`}
          aria-label={title}
          role="img"
          className="overflow-visible filter drop-shadow-sm"
        >
          {normalised.map((item, i) => {
            const y = PAD + i * ROW_H;
            const barW = Math.max((item.score / maxScore) * (BAR_AREA - 48), 4);
            const color = barColor(item.score);
            const labelY = y + ROW_H / 2;

            return (
              <g key={item.label} aria-label={`${item.label}: ${item.score}`}>
                {/* Query / keyword label */}
                <text
                  x={LABEL_W - 8}
                  y={labelY + 4}
                  textAnchor="end"
                  fontSize="11"
                  fill="currentColor"
                  className="fill-slate-500 dark:fill-slate-400"
                  style={{ fontFamily: "Inter, sans-serif" }}
                >
                  {item.label.length > 25
                    ? item.label.slice(0, 24) + "…"
                    : item.label}
                </text>

                {/* Bar background track */}
                <rect
                  x={LABEL_W}
                  y={y + 12}
                  width={BAR_AREA - 48}
                  height={16}
                  rx={8}
                  className="fill-slate-100 dark:fill-slate-700"
                />

                {/* Filled bar */}
                <rect
                  x={LABEL_W}
                  y={y + 12}
                  width={barW}
                  height={16}
                  rx={8}
                  fill={color}
                  opacity={0.85}
                />

                {/* Score number */}
                <text
                  x={LABEL_W + (BAR_AREA - 44)}
                  y={labelY + 4}
                  textAnchor="start"
                  fontSize="11"
                  fontWeight="600"
                  fill={color}
                  style={{ fontFamily: "IBM Plex Mono, monospace" }}
                >
                  {item.score}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 mt-3 pt-3 border-t
        border-slate-100 dark:border-slate-700">
        {[
          { color: "#34d399", label: "70–100  High" },
          { color: "#fbbf24", label: "40–69   Mid" },
          { color: "#94a3b8", label: "0–39    Low" },
        ].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full flex-shrink-0"
              style={{ backgroundColor: color }} />
            <span className="text-[11px] font-mono text-slate-400">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
