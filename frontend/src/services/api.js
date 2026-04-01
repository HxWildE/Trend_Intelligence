const BASE_URL = "http://127.0.0.1:8080";

/**
 * searchQuery – POST a search term to the backend and get its ML trend score.
 * Backend returns: { query, trend_score, message }
 */
export const searchQuery = async (q) => {
  const res = await fetch(`${BASE_URL}/search?q=${encodeURIComponent(q)}`);
  if (!res.ok) throw new Error(`Search failed: ${res.status}`);
  return res.json();
};

/**
 * getTrends – fetch the top global trending topics from the latest ML run.
 * Backend returns: { trends: [...], run_at: "..." }
 * We unwrap .trends so pages receive a plain array.
 */
export const getTrends = async () => {
  const res = await fetch(`${BASE_URL}/trends`);
  if (!res.ok) throw new Error(`Failed to fetch trends: ${res.status}`);
  const data = await res.json();
  // Backend wraps results in { trends: [...] } — unwrap for the frontend
  return Array.isArray(data) ? data : (data.trends ?? []);
};

/**
 * getRegionTrends – fetch trending topics filtered by an Indian state.
 * Backend returns: { state, trends: [...], run_at: "..." }
 * We unwrap .trends so IndiaTrends.jsx receives a plain array.
 */
export const getRegionTrends = async (state) => {
  const res = await fetch(`${BASE_URL}/region?state=${encodeURIComponent(state)}`);
  if (!res.ok) throw new Error(`Failed to fetch region trends: ${res.status}`);
  const data = await res.json();
  // Backend wraps results in { state, trends: [...] } — unwrap for the frontend
  return Array.isArray(data) ? data : (data.trends ?? []);
};