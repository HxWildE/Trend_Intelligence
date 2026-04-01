import React, { useEffect, useState } from "react";

export default function NewsFeed({ region, topic }) {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNews = async () => {
      setLoading(true);
      try {
        let url = `http://127.0.0.1:8080/news/realtime`;
        if (topic) {
          url += `?topic=${encodeURIComponent(topic)}`;
        } else if (region && region !== "India") {
          url += `?region=${encodeURIComponent(region)}`;
        }
        
        const res = await fetch(url);
        const data = await res.json();
        setNews(data);
      } catch (e) {
        console.error("Failed to fetch news:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchNews();
  }, [region, topic]);

  if (loading) {
    return (
      <div className="mb-10 w-full">
         <div className="flex items-center gap-2 mb-4 animate-fade-up">
            <span className="text-xl">📰</span>
            <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100">
              {topic ? `Live News for "${topic}"` : region && region !== "India" ? `Live ${region} News` : "Live Global News"}
            </h3>
         </div>
         <div className="flex gap-4 overflow-x-auto pb-4 hide-scrollbar">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="skeleton shrink-0 w-80 h-40 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (news.length === 0) return null;

  return (
    <div className="mb-10 w-full animate-fade-up border-b border-slate-200 dark:border-slate-800 pb-10">
      <div className="flex items-center gap-2 mb-6">
        <span className="text-2xl">📰</span>
        <h3 className="text-xl font-extrabold tracking-tight text-slate-900 dark:text-slate-100">
          {topic ? `Live News for "${topic}"` : region && region !== "India" ? `Live ${region} News` : "Live Global News"}
        </h3>
        <span className="px-2.5 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-600 dark:text-blue-400 text-xs font-bold ml-auto shadow-sm">
          ✨ AI Summarized
        </span>
      </div>
      
      <div className="flex gap-5 overflow-x-auto pb-4 snap-x" style={{scrollbarWidth: 'none', msOverflowStyle: 'none'}}>
        {news.map((item, i) => (
          <a
            key={i}
            href={item.url}
            target="_blank"
            rel="noreferrer"
            className="shrink-0 w-[340px] p-6 rounded-2xl border transition-all duration-300
              snap-center flex flex-col
              text-slate-700 dark:text-slate-300 bg-white/50 dark:bg-slate-800/30 backdrop-blur-sm
              border-slate-200/60 dark:border-slate-700/50 
              hover:bg-white dark:hover:bg-slate-800
              hover:shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:hover:shadow-[0_8px_30px_rgba(0,0,0,0.2)] 
              hover:-translate-y-1 hover:border-blue-500/30 group"
          >
            <div className="flex items-center gap-3 mb-4 text-xs font-medium">
              <span className={`px-2.5 py-1 rounded-lg ${
                item.source.includes("Hacker") 
                  ? "bg-orange-500/10 text-orange-600 dark:text-orange-400" 
                  : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
              }`}>
                {item.source}
              </span>
              <span className="text-slate-400/80 font-mono">
                {new Date(item.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
              </span>
            </div>
            
            <h4 className="text-base font-bold text-slate-900 dark:text-white leading-snug mb-3 line-clamp-2 group-hover:text-blue-500 transition-colors">
              {item.title}
            </h4>
            
            <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-3 leading-relaxed mt-auto border-t border-slate-100 dark:border-slate-700/50 pt-3">
              {item.summary || "No summary available."}
            </p>
          </a>
        ))}
      </div>
    </div>
  );
}
