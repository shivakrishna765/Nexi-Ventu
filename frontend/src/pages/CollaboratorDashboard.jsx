/**
 * CollaboratorDashboard — Pink/rose theme
 * Shows: co-founder suggestions, networking cards, collaboration invites
 */
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Handshake, Network, UserPlus, Sparkles } from "lucide-react";
import Chatbot from "../components/Chatbot";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";

function StatCard({ icon: Icon, label, value, sub }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className="rounded-2xl border border-pink-500/20 bg-gradient-to-br from-pink-950/40 to-slate-900/60 p-5"
    >
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-pink-600">
        <Icon size={18} className="text-white" />
      </div>
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-bold text-pink-300">{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </motion.div>
  );
}

function MatchCard({ match, idx }) {
  const score = match.match_score ?? 0;
  const isFounder = match.type === "founder";
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: idx * 0.07 }}
      whileHover={{ y: -2 }}
      className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-4"
    >
      <div className="flex items-start gap-3">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-pink-600 to-rose-500 text-lg font-bold text-white">
          {match.name?.[0] || "?"}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2">
            <p className="font-semibold text-white truncate">{match.name}</p>
            <span className="shrink-0 rounded-full bg-pink-500/20 px-2 py-0.5 text-xs text-pink-300">
              {score}%
            </span>
          </div>
          <p className="text-xs text-pink-400/80 capitalize">{match.type}</p>
          {match.skills && (
            <p className="mt-1 text-xs text-slate-400 line-clamp-1">Skills: {match.skills}</p>
          )}
          {match.domain && (
            <p className="text-xs text-slate-400">Domain: {match.domain}</p>
          )}
        </div>
      </div>

      {match.reasons?.length > 0 && (
        <div className="mt-3 rounded-xl bg-slate-800/60 px-3 py-2 text-xs text-slate-400">
          <span className="text-pink-400">Why match: </span>{match.reasons[0]}
        </div>
      )}

      <div className="mt-3 flex gap-2">
        <button className="flex-1 rounded-xl border border-pink-500/40 py-1.5 text-xs text-pink-300 hover:bg-pink-500/10 transition-colors">
          Connect
        </button>
        <button className="flex-1 rounded-xl border border-slate-700 py-1.5 text-xs text-slate-400 hover:bg-slate-800 transition-colors">
          View Profile
        </button>
      </div>
    </motion.div>
  );
}

export default function CollaboratorDashboard() {
  const { user } = useAuth();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.chatDemo({
      query: "find co-founders and collaboration partners",
      role: "collaborator",
      skills: user?.skills || user?.bio || "react node.js python",
      interests: user?.interests || "Fintech EdTech",
      top_n: 8,
    })
      .then((d) => setMatches(d.results || []))
      .catch(() => setMatches([]))
      .finally(() => setLoading(false));
  }, [user]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 md:px-8">
      <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <p className="text-sm text-pink-400/80">Collaborator Dashboard</p>
        <h1 className="text-3xl font-bold text-white">
          Find your <span className="text-pink-300">co-founder</span>
        </h1>
        <p className="mt-1 text-slate-400">Discover founders and startups aligned with your vision and skills.</p>
      </motion.div>

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Handshake} label="Co-Founder Compat."  value="91%"  sub="Profile alignment" />
        <StatCard icon={Network}   label="Network Strength"    value="High" sub="Active connections" />
        <StatCard icon={UserPlus}  label="Pending Invites"     value="5"    sub="Awaiting response" />
        <StatCard icon={Sparkles}  label="Partnership Score"   value="88%"  sub="Based on interests" />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        <div>
          <h2 className="mb-4 font-semibold text-white">Suggested Co-Founders & Partners</h2>
          {loading ? (
            <div className="grid gap-4 md:grid-cols-2">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-44 animate-pulse rounded-2xl bg-slate-800/60" />
              ))}
            </div>
          ) : matches.length === 0 ? (
            <p className="text-slate-400">No matches yet. Update your profile to improve results.</p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {matches.map((m, i) => <MatchCard key={m.id || i} match={m} idx={i} />)}
            </div>
          )}
        </div>

        <Chatbot role="collaborator" />
      </div>
    </div>
  );
}
