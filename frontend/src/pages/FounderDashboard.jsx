/**
 * FounderDashboard — Violet/indigo futuristic theme
 * Shows: startup overview, investor recommendations, team suggestions, growth metrics
 */
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Rocket, Users, TrendingUp, Lightbulb, CheckCircle2, Circle } from "lucide-react";
import Chatbot from "../components/Chatbot";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";

const MILESTONES = [
  { label: "Profile completed",        done: true  },
  { label: "Startup idea submitted",   done: true  },
  { label: "First investor match",     done: false },
  { label: "Team member onboarded",    done: false },
  { label: "Seed funding secured",     done: false },
];

function StatCard({ icon: Icon, label, value, sub }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className="rounded-2xl border border-violet-500/20 bg-gradient-to-br from-violet-950/40 to-slate-900/60 p-5"
    >
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-violet-600">
        <Icon size={18} className="text-white" />
      </div>
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-bold text-violet-300">{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </motion.div>
  );
}

function InvestorCard({ investor, idx }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: idx * 0.07 }}
      className="flex items-center gap-3 rounded-xl border border-slate-700/60 bg-slate-900/60 p-3"
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-indigo-500 text-sm font-bold text-white">
        {investor.name?.[0] || "I"}
      </div>
      <div className="min-w-0 flex-1">
        <p className="truncate font-medium text-white">{investor.name}</p>
        <p className="truncate text-xs text-slate-400">{investor.interests || investor.domain || "Investor"}</p>
      </div>
      <span className="shrink-0 rounded-full bg-violet-500/20 px-2 py-0.5 text-xs text-violet-300">
        {investor.match_score || "—"}%
      </span>
    </motion.div>
  );
}

export default function FounderDashboard() {
  const { user } = useAuth();
  const [investors, setInvestors] = useState([]);

  useEffect(() => {
    // Use chatbot demo to get investor suggestions
    api.chatDemo({
      query: "find investors for my startup",
      role: "founder",
      skills: user?.skills || user?.bio || "product machine learning",
      interests: user?.interests || "AI Healthcare",
      top_n: 6,
    })
      .then((d) => setInvestors(d.results || []))
      .catch(() => setInvestors([]));
  }, [user]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 md:px-8">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <p className="text-sm text-violet-400/80">Founder Dashboard</p>
        <h1 className="text-3xl font-bold text-white">
          Build with <span className="text-violet-300">{user?.name?.split(" ")[0]}</span>
        </h1>
        <p className="mt-1 text-slate-400">Define your vision, find your team, and connect with the right investors.</p>
      </motion.div>

      {/* KPIs */}
      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard icon={Rocket}     label="Startup Stage"      value="Seed"   sub="Ready for funding" />
        <StatCard icon={Users}      label="Team Completion"    value="40%"    sub="2 of 5 roles filled" />
        <StatCard icon={TrendingUp} label="Investor Interest"  value="18"     sub="Profile views this week" />
        <StatCard icon={Lightbulb}  label="Idea Score"         value="82/100" sub="Based on market fit" />
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_380px]">
        <div className="space-y-6">
          {/* Progress tracker */}
          <div className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-5">
            <h2 className="mb-4 font-semibold text-white">Startup Progress Tracker</h2>
            <div className="space-y-3">
              {MILESTONES.map((m, i) => (
                <div key={i} className="flex items-center gap-3">
                  {m.done
                    ? <CheckCircle2 size={18} className="shrink-0 text-emerald-400" />
                    : <Circle size={18} className="shrink-0 text-slate-600" />
                  }
                  <span className={`text-sm ${m.done ? "text-white" : "text-slate-500"}`}>{m.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Suggested investors */}
          <div className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-5">
            <h2 className="mb-4 font-semibold text-white">Suggested Investors</h2>
            {investors.length === 0 ? (
              <p className="text-sm text-slate-400">Loading investor matches…</p>
            ) : (
              <div className="space-y-2">
                {investors.map((inv, i) => (
                  <InvestorCard key={inv.id || i} investor={inv} idx={i} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Chatbot */}
        <Chatbot role="founder" />
      </div>
    </div>
  );
}
