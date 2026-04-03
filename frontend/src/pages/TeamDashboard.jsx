/**
 * TeamDashboard — Emerald/green theme for Team Seekers
 * Shows: startup cards with match %, skills alignment, domain match
 */
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Search, Briefcase, Code2, MapPin, Zap } from "lucide-react";
import Chatbot from "../components/Chatbot";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";

function StatCard({ icon: Icon, label, value, sub }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className="rounded-2xl border border-emerald-500/20 bg-gradient-to-br from-emerald-950/40 to-slate-900/60 p-5"
    >
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600">
        <Icon size={18} className="text-white" />
      </div>
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-bold text-emerald-300">{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </motion.div>
  );
}

function StartupCard({ startup, idx }) {
  const score = startup.match_score ?? startup.match ?? 0;
  const barW  = Math.min(score, 100);
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
          <p className="text-xs text-emerald-400/80 uppercase tracking-wide">{startup.domain || startup.type}</p>
          <h3 className="mt-0.5 font-semibold text-white">{startup.name}</h3>
        </div>
        <span className="shrink-0 rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs text-emerald-300">
          {score}% match
        </span>
      </div>

      {/* Match bar */}
      <div className="mt-3 h-1.5 w-full rounded-full bg-slate-800">
        <div
          className="h-1.5 rounded-full bg-gradient-to-r from-emerald-500 to-cyan-400 transition-all"
          style={{ width: `${barW}%` }}
        />
      </div>

      {startup.required_skills && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {startup.required_skills.split(/[,\s]+/).filter(Boolean).slice(0, 4).map((sk) => (
            <span key={sk} className="rounded-full border border-emerald-700/40 bg-emerald-900/20 px-2 py-0.5 text-xs text-emerald-300">
              {sk}
            </span>
          ))}
        </div>
      )}

      {startup.reasons?.length > 0 && (
        <p className="mt-2 text-xs text-slate-400">
          <span className="text-cyan-400">Why:</span> {startup.reasons[0]}
        </p>
      )}

      <div className="mt-3 flex gap-2 text-xs text-slate-500">
        {startup.funding_stage && <span>💰 {startup.funding_stage}</span>}
        {startup.location && <span>📍 {startup.location}</span>}
      </div>
    </motion.div>
  );
}

export default function TeamDashboard() {
  const { user } = useAuth();
  const [matches, setMatches] = useState([]);
  const [search, setSearch]   = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.chatDemo({
      query: "find startups matching my skills",
      role: "seeker",
      skills: user?.skills || user?.bio || "python machine learning",
      interests: user?.interests || "AI Healthcare",
      top_n: 8,
    })
      .then((d) => setMatches(d.results || []))
      .catch(() => setMatches([]))
      .finally(() => setLoading(false));
  }, [user]);

  const filtered = matches.filter((m) =>
    !search || m.name?.toLowerCase().includes(search.toLowerCase()) ||
    m.domain?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 md:px-8">
      <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <p className="text-sm text-emerald-400/80">Team Seeker Dashboard</p>
        <h1 className="text-3xl font-bold text-white">
          Find your <span className="text-emerald-300">perfect startup</span>
        </h1>
        <p className="mt-1 text-slate-400">Startups matched to your skills, experience, and domain interests.</p>
      </motion.div>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Zap}       label="Opportunity Match"   value="94%"  sub="Profile alignment score" />
        <StatCard icon={Code2}     label="Skill Relevance"     value="High" sub="Based on your stack" />
        <StatCard icon={Briefcase} label="Open Roles"          value="38"   sub="Across matched startups" />
        <StatCard icon={MapPin}    label="Nearby Startups"     value="12"   sub="In your location" />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        <div>
          {/* Search */}
          <div className="mb-4 flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900/60 px-3 py-2">
            <Search size={14} className="text-slate-400" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by startup name or domain…"
              className="flex-1 bg-transparent text-sm outline-none placeholder:text-slate-500"
            />
          </div>

          {loading ? (
            <div className="grid gap-4 md:grid-cols-2">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-40 animate-pulse rounded-2xl bg-slate-800/60" />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <p className="text-slate-400">No matches found. Try updating your profile skills.</p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {filtered.map((s, i) => <StartupCard key={s.id || i} startup={s} idx={i} />)}
            </div>
          )}
        </div>

        <Chatbot role="seeker" />
      </div>
    </div>
  );
}
