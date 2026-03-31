/**
 * SearchBar.jsx
 *
 * Purely presentational search input component. It owns ZERO state — the
 * parent page (Search.jsx) controls the value and fires the search action.
 * Responsibility: render the search box UI and forward user interactions upward.
 *
 * Props:
 *   value       – string  – controlled input value (from parent state)
 *   onChange    – fn      – called on every keystroke: (newValue: string) => void
 *   onSearch    – fn      – called when user clicks Search or presses Enter: () => void
 *   loading     – boolean – disables the button and shows loading text
 *   placeholder – string  – optional placeholder text
 */

import React from "react";

const IconSearch = () => (
  <svg
    width="20" height="20"
    className="w-5 h-5 text-slate-400 flex-shrink-0"
    viewBox="0 0 24 24" fill="none"
    stroke="currentColor" strokeWidth="2"
    strokeLinecap="round" strokeLinejoin="round"
  >
    <circle cx="11" cy="11" r="8" />
    <path d="m21 21-4.35-4.35" />
  </svg>
);

export default function SearchBar({
  value,
  onChange,
  onSearch,
  loading = false,
  placeholder = "e.g. IPL 2026, AI tools, Budget…",
}) {
  /**
   * handleKey – intercepts Enter key press inside the input and
   * delegates to the parent's onSearch callback.
   */
  const handleKey = (e) => {
    if (e.key === "Enter") onSearch();
  };

  return (
    <div
      className="flex items-center gap-0 max-w-xl mx-auto rounded-2xl overflow-hidden
        border border-slate-200 dark:border-slate-700 transition-all duration-200 glow-focus
        bg-white dark:bg-slate-800/80 shadow-card"
    >
      {/* Left icon */}
      <div className="pl-4 flex-shrink-0">
        <IconSearch />
      </div>

      {/* Controlled text input */}
      <input
        id="search-input"
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKey}
        placeholder={placeholder}
        autoComplete="off"
        className="flex-1 bg-transparent outline-none py-3 px-3 text-sm font-medium
          text-slate-800 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500"
      />

      {/* Search button */}
      <button
        id="search-btn"
        onClick={onSearch}
        disabled={loading}
        className="m-1.5 px-5 py-2.5 rounded-xl text-sm font-semibold text-white
          btn-accent transition-all duration-200 shadow-glow-sm hover:shadow-glow-md
          hover:-translate-y-px active:translate-y-0
          disabled:opacity-60 disabled:cursor-not-allowed"
      >
        {loading ? "Searching…" : "Search →"}
      </button>
    </div>
  );
}
