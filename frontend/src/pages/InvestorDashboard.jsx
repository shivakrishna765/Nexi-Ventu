/**
 * InvestorDashboard — Gold/dark theme
 * Shows: recommended startups, risk analysis, funding stage filters, market trends
 */
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { TrendingUp, DollarSign, BarChart3, Filter, Star } from "lucide-react";
import Chatbot from "../components/Chatbot";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";

const STAGES = ["All", "Pre-Seed", "Seed", "Series A", "Series B"];
const DOMAINS = ["All", "AI", "Healthcare", "Fintech", "CleanTech", "AgriTech", "EdTech"];

const RISK_COLOR = { low: "text-emerald-400", medium: "text-amber-400", high: "text-red-400" };

function StatCard({ icon: Icon, label, value, sub, accent }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className="rounded-2xl border border-amber-500/20 bg-gradient-to-br from-amber-950/40 to-slate-900/60 p-5"
    >
      <div className={`mb-3 flex h-10 w-10 items-center justify-center rounded-xl ${accent}`}>
        <Icon size={18} className="text-white" />
      </div>
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-bold text-amber-300">{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </motion.div>
  );
}

function StartupCard({ startup, idx }) {
  const riskColor = RISK_COLOR[startup.risk_level] || "text-slate-400";
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: idx * 0.06 }}
      whileHover={{ y: -2 }}
      className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-4 backdrop-blur-sm"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs text-amber-400/80 uppercase tracking-wide">{startup.domain}</p>
          <h3 className="mt-0.5 font-semibold text-white">{startup.name}</h3>
        </div>
        <span className="shrink-0 rounded-full bg-amber-500/20 px-2 py-0.5 text-xs text-amber-300">
          {startup.match || startup.traction_score || "—"}% match
        </span>
      </div>
      <p className="mt-2 text-sm text-slate-400 line-clamp-2">{startup.description}</p>
      <div className="mt-3 flex flex-wrap gap-2 text-xs">
        <span className="rounded-full border border-slate-700 px-2 py-0.5 text-slate-400">
          {startup.funding_stage || "Seed"}
        </span>
        {startup.risk_level && (
          <span className={`rounded-full border border-slate-700 px-2 py-0.5 ${riskColor}`}>
            {startup.risk_level} risk
          </span>
        )}
        {startup.location && (
          <span className="rounded-full border border-slate-700 px-2 py-0.5 text-slate-400">
            📍 {startup.location}
          </span>
        )}
      </div>
    </motion.div>
  );
}

export default function InvestorDashboard() {
  const { user } = useAuth();
  const [startups, setStartups] = useState([]);
  const [stage, setStage]       = useState("All");
  const [domain, setDomain]     = useState("All");
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    api.getStartups()
      .then(setStartups)
      .catch(() => setStartups([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = startups.filter((s) => {
    const okStage  = stage  === "All" || (s.funding_stage || "").toLowerCase().includes(stage.toLowerCase());
    const okDomain = domain === "All" || (s.domain || "").toLowerCase().includes(domain.toLowerCase());
    return okStage && okDomain;
  });

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 md:px-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <p className="text-sm text-amber-400/80">Investor Dashboard</p>
        <h1 className="text-3xl font-bold text-white">
          Welcome back, <span className="text-amber-300">{user?.name?.split(" ")[0]}</span>
        </h1>
        <p className="mt-1 text-slate-400">Discover high-potential startups based on your investment profile.</p>
      </motion.div>

      {/* KPI Stats */}
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={DollarSign}  label="Portfolio Value"    value="₹4.2Cr"  sub="Across 8 startups"       accent="bg-amber-600" />
        <StatCard icon={TrendingUp}  label="Avg Match Score"    value="87%"     sub="Based on your interests"  accent="bg-yellow-600" />
        <StatCard icon={BarChart3}   label="Active Deals"       value="12"      sub="3 pending review"         accent="bg-orange-600" />
        <StatCard icon={Star}        label="Watchlist"          value="24"      sub="Startups saved"           accent="bg-red-700" />
      </div>

      {/* Main grid */}
      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        {/* Startup recommendations */}
        <div>
          {/* Filters */}
          <div className="mb-4 flex flex-wrap items-center gap-2">
            <Filter size={14} className="text-slate-400" />
            <div className="flex flex-wrap gap-1.5">
              {STAGES.map((s) => (
                <button
                  key={s}
                  onClick={() => setStage(s)}
                  className={`rounded-full px-3 py-1 text-xs transition-all ${
                    stage === s
                      ? "bg-amber-500 text-white"
                      : "border border-slate-700 text-slate-400 hover:border-amber-500/50"
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap gap-1.5">
              {DOMAINS.map((d) => (
                <button
                  key={d}
                  onClick={() => setDomain(d)}
                  className={`rounded-full px-3 py-1 text-xs transition-all ${
                    domain === d
                      ? "bg-yellow-600 text-white"
                      : "border border-slate-700 text-slate-400 hover:border-yellow-500/50"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {loading ? (
            <div className="grid gap-4 md:grid-cols-2">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-36 animate-pulse rounded-2xl bg-slate-800/60" />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <p className="text-slate-400">No startups match your current filters.</p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {filtered.slice(0, 8).map((s, i) => (
                <StartupCard key={s.id || i} startup={s} idx={i} />
              ))}
            </div>
          )}
        </div>

        {/* Chatbot */}
        <Chatbot role="investor" />
      </div>
    </div>
  );
}
