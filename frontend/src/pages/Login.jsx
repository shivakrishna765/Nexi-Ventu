import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../context/AuthContext";
import { roleToRoute } from "../utils/session";

const ROLES = [
  { value: "investor",     label: "Investor",     desc: "Discover & fund high-potential startups" },
  { value: "founder",      label: "Founder",      desc: "Build your startup, find team & investors" },
  { value: "seeker",       label: "Team Seeker",  desc: "Find startups that match your skills" },
  { value: "collaborator", label: "Collaborator", desc: "Find co-founders & strategic partners" },
];

export default function Login() {
  const [mode, setMode]       = useState("login");
  const [role, setRole]       = useState("investor");
  const [name, setName]       = useState("");
  const [email, setEmail]     = useState("");
  const [password, setPassword] = useState("");
  const [error, setError]     = useState("");
  const [loading, setLoading] = useState(false);

  const { login, signup } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname;

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      let user;
      if (mode === "login") {
        user = await login(email, password);
      } else {
        user = await signup(name, email, password, role);
      }
      navigate(from || roleToRoute(user.role), { replace: true });
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4 py-16">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Card */}
        <div className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-8 shadow-2xl backdrop-blur-sm">
          {/* Header */}
          <div className="mb-6 text-center">
            <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 text-lg font-black text-white">
              NV
            </div>
            <h1 className="text-2xl font-bold">
              {mode === "login" ? "Welcome back" : "Join Nexus Venture"}
            </h1>
            <p className="mt-1 text-sm text-slate-400">
              {mode === "login"
                ? "Sign in to access your personalised dashboard"
                : "Create your account and choose your role"}
            </p>
          </div>

          {/* Mode toggle */}
          <div className="mb-6 flex rounded-xl border border-slate-700 p-1">
            {["login", "signup"].map((m) => (
              <button
                key={m}
                onClick={() => { setMode(m); setError(""); }}
                className={`flex-1 rounded-lg py-1.5 text-sm font-medium transition-all ${
                  mode === m
                    ? "bg-gradient-to-r from-violet-600 to-cyan-500 text-white"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {m === "login" ? "Sign In" : "Sign Up"}
              </button>
            ))}
          </div>

          <form onSubmit={submit} className="space-y-4">
            {mode === "signup" && (
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Full name"
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-950/60 px-4 py-2.5 text-sm outline-none focus:border-violet-500 transition-colors"
              />
            )}
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email address"
              required
              className="w-full rounded-xl border border-slate-700 bg-slate-950/60 px-4 py-2.5 text-sm outline-none focus:border-violet-500 transition-colors"
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              required
              className="w-full rounded-xl border border-slate-700 bg-slate-950/60 px-4 py-2.5 text-sm outline-none focus:border-violet-500 transition-colors"
            />

            {/* Role selector — signup only */}
            {mode === "signup" && (
              <div className="space-y-2">
                <p className="text-xs font-medium text-slate-400 uppercase tracking-wide">Select your role</p>
                <div className="grid grid-cols-2 gap-2">
                  {ROLES.map((r) => (
                    <button
                      key={r.value}
                      type="button"
                      onClick={() => setRole(r.value)}
                      className={`rounded-xl border p-3 text-left text-xs transition-all ${
                        role === r.value
                          ? "border-violet-500 bg-violet-500/15 text-white"
                          : "border-slate-700 text-slate-400 hover:border-slate-500"
                      }`}
                    >
                      <p className="font-semibold">{r.label}</p>
                      <p className="mt-0.5 text-slate-500 leading-tight">{r.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {error && (
              <p className="rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-400">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 py-2.5 font-semibold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {loading ? "Please wait…" : mode === "login" ? "Sign In" : "Create Account"}
            </button>
          </form>

          {/* OAuth hint */}
          <div className="mt-5 border-t border-slate-800 pt-5">
            <p className="mb-3 text-center text-xs text-slate-500">Or continue with</p>
            <div className="flex gap-3">
              {["Google", "LinkedIn"].map((provider) => (
                <button
                  key={provider}
                  disabled
                  title="OAuth coming soon"
                  className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-slate-700 py-2 text-sm text-slate-400 opacity-50 cursor-not-allowed"
                >
                  {provider}
                </button>
              ))}
            </div>
            <p className="mt-2 text-center text-xs text-slate-600">OAuth integration — coming soon</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
