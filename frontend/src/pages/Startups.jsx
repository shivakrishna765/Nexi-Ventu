import { useMemo, useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Search, SlidersHorizontal } from "lucide-react";
import { api } from "../utils/api";

const STAGES  = ["All", "Pre-Seed", "Seed", "Series A", "Series B"];
const DOMAINS = ["All", "AI", "Healthcare", "Fintech", "CleanTech", "AgriTech", "EdTech", "Logistics", "HRTech"];

const DOMAIN_COLORS = {
  ai:         "from-violet-600 to-indigo-500",
  healthcare: "from-emerald-600 to-teal-500",
  fintech:    "from-amber-600 to-yellow-500",
  cleantech:  "from-green-600 to-lime-500",
  agritech:   "from-lime-600 to-green-500",
  edtech:     "from-orange-600 to-amber-500",
  logistics:  "from-blue-600 to-cyan-500",
  hrtech:     "from-pink-600 to-rose-500",
};

function domainGradient(domain = "") {
  const key = domain.toLowerCase().replace(/[^a-z]/g, "");
  return DOMAIN_COLORS[key] || "from-slate-600 to-slate-500";
}

function StartupCard({ startup, idx }) {
  const grad = domainGradient(startup.domain);
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: idx * 0.05 }}
      whileHover={{ y: -3 }}
      className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-5 backdrop-blur-sm"
    >
      <div className={`mb-3 inline-flex items-center gap-1.5 rounded-full bg-gradient-to-r ${grad} px-2.5 py-0.5 text-xs font-medium text-white`}>
        {startup.domain || "Startup"}
      </div>
      <h3 className="text-lg font-semibold text-white">{startup.name}</h3>
      <p className="mt-2 text-sm text-slate-400 line-clamp-2">{startup.description}</p>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-xs">
        <span className="rounded-full border border-slate-700 px-2.5 py-1 text-slate-400">
          {startup.funding_stage || "Seed"}
        </span>
        {(startup.match || startup.traction_score) && (
          <span className="rounded-full bg-violet-500/20 px-2.5 py-1 text-violet-300">
            {startup.match || Math.round(startup.traction_score)}% match
          </span>
        )}
      </div>
    </motion.div>
  );
}

export default function Startups() {
  const [startups, setStartups] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [search, setSearch]     = useState("");
  const [stage, setStage]       = useState("All");
  const [domain, setDomain]     = useState("All");

  useEffect(() => {
    api.getStartups()
      .then(setStartups)
      .catch(() => setStartups([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    return startups.filter((s) => {
      const q = search.toLowerCase();
      const okSearch = !q || s.name?.toLowerCase().includes(q) || s.domain?.toLowerCase().includes(q) || s.description?.toLowerCase().includes(q);
      const okStage  = stage  === "All" || (s.funding_stage || "").toLowerCase().includes(stage.toLowerCase());
      const okDomain = domain === "All" || (s.domain || "").toLowerCase().includes(domain.toLowerCase());
      return okSearch && okStage && okDomain;
    });
  }, [startups, search, stage, domain]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-8">
      <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h1 className="text-3xl font-bold text-white">Startup Directory</h1>
        <p className="mt-1 text-slate-400">Explore startups across domains and funding stages.</p>
      </motion.div>

      {/* Filters */}
      <div className="mb-6 space-y-3">
        <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2.5">
          <Search size={14} className="text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name, domain, or description…"
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-slate-500"
          />
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <SlidersHorizontal size={14} className="text-slate-400" />
          {STAGES.map((s) => (
            <button key={s} onClick={() => setStage(s)}
              className={`rounded-full px-3 py-1 text-xs transition-all ${stage === s ? "bg-violet-600 text-white" : "border border-slate-700 text-slate-400 hover:border-violet-500/50"}`}>
              {s}
            </button>
          ))}
          <span className="text-slate-700">|</span>
          {DOMAINS.map((d) => (
            <button key={d} onClick={() => setDomain(d)}
              className={`rounded-full px-3 py-1 text-xs transition-all ${domain === d ? "bg-cyan-600 text-white" : "border border-slate-700 text-slate-400 hover:border-cyan-500/50"}`}>
              {d}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-44 animate-pulse rounded-2xl bg-slate-800/60" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <p className="text-slate-400">No startups match your filters.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((s, i) => <StartupCard key={s.id || i} startup={s} idx={i} />)}
        </div>
      )}
    </div>
  );
}
