import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { Rocket, Brain, Users, TrendingUp, Shield, Zap } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { roleToRoute } from "../utils/session";

const FEATURES = [
  { icon: Brain,      title: "AI-Powered Matching",    desc: "TF-IDF + weighted scoring delivers precise startup-investor-talent matches.", color: "from-violet-600 to-indigo-500" },
  { icon: Rocket,     title: "Startup Discovery",      desc: "Browse and filter startups by domain, stage, and skill alignment.",          color: "from-cyan-600 to-blue-500" },
  { icon: Users,      title: "Multi-Role Platform",    desc: "Tailored dashboards for investors, founders, seekers, and collaborators.",    color: "from-emerald-600 to-teal-500" },
  { icon: TrendingUp, title: "Growth Intelligence",    desc: "Track funding stages, traction scores, and market signals in real time.",     color: "from-amber-600 to-yellow-500" },
  { icon: Shield,     title: "Secure & Role-Gated",    desc: "JWT auth with role-based access control — no cross-role data leakage.",      color: "from-pink-600 to-rose-500" },
  { icon: Zap,        title: "Conversational AI",      desc: "Chat with Nexus AI to get personalised recommendations instantly.",          color: "from-orange-600 to-red-500" },
];

const ROLES = [
  { role: "investor",     label: "Investor",     desc: "Discover high-potential startups",    color: "border-amber-500/40 hover:border-amber-400",  dot: "bg-amber-400" },
  { role: "founder",      label: "Founder",      desc: "Build your team & find funding",      color: "border-violet-500/40 hover:border-violet-400", dot: "bg-violet-400" },
  { role: "seeker",       label: "Team Seeker",  desc: "Join startups that match your skills", color: "border-emerald-500/40 hover:border-emerald-400", dot: "bg-emerald-400" },
  { role: "collaborator", label: "Collaborator", desc: "Find co-founders & partners",         color: "border-pink-500/40 hover:border-pink-400",     dot: "bg-pink-400" },
];

export default function Home() {
  const { user } = useAuth();

  return (
    <div className="overflow-hidden">
      {/* Hero */}
      <section className="mx-auto max-w-7xl px-4 py-24 md:px-8 md:py-32">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-4xl"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-1.5 text-sm text-violet-300"
          >
            <span className="h-1.5 w-1.5 rounded-full bg-violet-400 animate-pulse" />
            AI-Powered Startup Ecosystem
          </motion.div>

          <h1 className="bg-gradient-to-r from-white via-violet-200 to-cyan-300 bg-clip-text text-5xl font-extrabold leading-tight text-transparent md:text-7xl">
            Connect. Build.<br />Fund. Grow.
          </h1>
          <p className="mt-6 max-w-2xl text-lg text-slate-400 leading-relaxed">
            Nexus Venture is a unified startup ecosystem where founders, investors, and talent
            collaborate through AI-powered matching and conversational intelligence.
          </p>

          <div className="mt-10 flex flex-wrap gap-4">
            {user ? (
              <Link
                to={roleToRoute(user.role)}
                className="rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 px-6 py-3 font-semibold text-white hover:opacity-90 transition-opacity"
              >
                Go to Dashboard →
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 px-6 py-3 font-semibold text-white hover:opacity-90 transition-opacity"
                >
                  Get Started Free
                </Link>
                <Link
                  to="/login"
                  className="rounded-xl border border-slate-600 px-6 py-3 font-medium text-slate-300 hover:border-slate-400 hover:text-white transition-colors"
                >
                  Sign In
                </Link>
              </>
            )}
          </div>
        </motion.div>
      </section>

      {/* Role cards */}
      <section className="mx-auto max-w-7xl px-4 pb-16 md:px-8">
        <motion.h2
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          className="mb-8 text-center text-2xl font-bold text-white"
        >
          Built for every role in the ecosystem
        </motion.h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {ROLES.map((r, i) => (
            <motion.div
              key={r.role}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              whileHover={{ y: -4 }}
              className={`rounded-2xl border bg-slate-900/60 p-5 backdrop-blur-sm transition-colors ${r.color}`}
            >
              <div className={`mb-3 h-2.5 w-2.5 rounded-full ${r.dot}`} />
              <h3 className="font-semibold text-white">{r.label}</h3>
              <p className="mt-1 text-sm text-slate-400">{r.desc}</p>
              <Link
                to="/login"
                className="mt-4 inline-block text-xs text-slate-400 hover:text-white transition-colors"
              >
                Join as {r.label} →
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features grid */}
      <section className="mx-auto max-w-7xl px-4 pb-24 md:px-8">
        <motion.h2
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          className="mb-8 text-center text-2xl font-bold text-white"
        >
          Everything you need to grow
        </motion.h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }}
              whileHover={{ y: -3 }}
              className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-5 backdrop-blur-sm"
            >
              <div className={`mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${f.color}`}>
                <f.icon size={18} className="text-white" />
              </div>
              <h3 className="font-semibold text-white">{f.title}</h3>
              <p className="mt-2 text-sm text-slate-400 leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
