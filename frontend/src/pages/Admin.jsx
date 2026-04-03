/**
 * Admin Dashboard — only accessible to users with is_admin=true in DB.
 * The ProtectedRoute (adminOnly) blocks frontend access.
 * The /admin/stats backend endpoint also enforces is_admin via get_current_admin.
 */
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Users, Rocket, MessageSquare, ShieldAlert } from "lucide-react";
import { api } from "../utils/api";
import { useAuth } from "../context/AuthContext";

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <motion.div
      whileHover={{ y: -3 }}
      className={`rounded-2xl border ${color} bg-slate-900/60 p-5`}
    >
      <Icon size={20} className="mb-3 text-slate-300" />
      <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
      <p className="mt-1 text-3xl font-bold text-white">{value ?? "—"}</p>
    </motion.div>
  );
}

export default function Admin() {
  const { user } = useAuth();
  const [stats, setStats]   = useState(null);
  const [error, setError]   = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.adminStats()
      .then(setStats)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 md:px-8">
      <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-2">
          <ShieldAlert size={20} className="text-red-400" />
          <p className="text-sm text-red-400">Admin Access Only</p>
        </div>
        <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
        <p className="mt-1 text-slate-400">Logged in as <span className="text-white">{user?.email}</span></p>
      </motion.div>

      {error && (
        <div className="mb-6 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-2xl bg-slate-800/60" />
          ))}
        </div>
      ) : stats ? (
        <>
          <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard icon={Users}        label="Total Users"    value={stats.total_users}    color="border-violet-500/30" />
            <StatCard icon={Rocket}       label="Total Startups" value={stats.total_startups} color="border-cyan-500/30" />
            <StatCard icon={MessageSquare} label="Total Chats"   value={stats.total_chats}    color="border-emerald-500/30" />
            <StatCard icon={ShieldAlert}  label="Admin"          value="Active"               color="border-red-500/30" />
          </div>

          {/* Role breakdown */}
          <div className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-5">
            <h2 className="mb-4 font-semibold text-white">Role Breakdown</h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
              {Object.entries(stats.role_breakdown || {}).map(([role, count]) => (
                <div key={role} className="rounded-xl border border-slate-700 bg-slate-800/60 p-3 text-center">
                  <p className="text-xs capitalize text-slate-400">{role}</p>
                  <p className="mt-1 text-xl font-bold text-white">{count}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
