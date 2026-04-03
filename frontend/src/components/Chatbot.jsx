import { useState, useRef, useEffect } from "react";
import { SendHorizonal, Bot, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";

const ROLE_CONFIG = {
  investor: {
    greeting: (name) => `Hi ${name}! I'm your Nexus investment advisor. Tell me your domain interests and I'll surface high-potential startups for you.`,
    placeholder: "e.g. AI healthcare startups at seed stage…",
    accent: "from-amber-500 to-yellow-400",
  },
  founder: {
    greeting: (name) => `Welcome ${name}! Define your startup vision and I'll help you find the right team members and investors.`,
    placeholder: "e.g. Looking for ML engineers and fintech investors…",
    accent: "from-violet-500 to-indigo-400",
  },
  seeker: {
    greeting: (name) => `Hey ${name}! Share your skills and I'll match you with startups where you can make an impact.`,
    placeholder: "e.g. Python developer interested in healthtech…",
    accent: "from-emerald-500 to-cyan-400",
  },
  member: {
    greeting: (name) => `Hey ${name}! Share your skills and I'll match you with startups where you can make an impact.`,
    placeholder: "e.g. Python developer interested in healthtech…",
    accent: "from-emerald-500 to-cyan-400",
  },
  collaborator: {
    greeting: (name) => `Hi ${name}! I'll help you find co-founders and collaboration opportunities that align with your vision.`,
    placeholder: "e.g. Full-stack dev looking for a fintech co-founder…",
    accent: "from-pink-500 to-rose-400",
  },
};

function MatchCard({ result }) {
  return (
    <div className="mt-2 rounded-xl border border-slate-700/60 bg-slate-800/60 p-3 text-xs">
      <div className="flex items-center justify-between">
        <span className="font-semibold text-white">{result.name}</span>
        <span className="rounded-full bg-violet-500/25 px-2 py-0.5 text-violet-300">
          {result.match_score}% match
        </span>
      </div>
      {result.domain && <p className="mt-1 text-slate-400">Domain: {result.domain}</p>}
      {result.funding_stage && <p className="text-slate-400">Stage: {result.funding_stage}</p>}
      {result.reasons?.length > 0 && (
        <ul className="mt-1.5 space-y-0.5 text-slate-400">
          {result.reasons.slice(0, 3).map((r, i) => (
            <li key={i} className="flex gap-1">
              <span className="text-cyan-400">•</span> {r}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function Chatbot({ role: propRole }) {
  const { user } = useAuth();
  const role = propRole || user?.role || "seeker";
  const cfg  = ROLE_CONFIG[role] || ROLE_CONFIG.seeker;
  const firstName = user?.name?.split(" ")[0] || "there";

  const [messages, setMessages] = useState([
    { id: 0, from: "bot", text: cfg.greeting(firstName), results: [] },
  ]);
  const [input, setInput]   = useState("");
  const [busy, setBusy]     = useState(false);
  const bottomRef           = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (e) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || busy) return;

    setInput("");
    setMessages((p) => [...p, { id: Date.now(), from: "user", text, results: [] }]);
    setBusy(true);

    try {
      const payload = {
        query:    text,
        role:     role,
        skills:   user?.skills || user?.bio || "",
        interests: user?.interests || "",
        location: user?.location || "",
        top_n:    5,
      };

      // Use demo endpoint if no token (shouldn't happen with ProtectedRoute, but safe)
      const data = user
        ? await api.chat(payload)
        : await api.chatDemo(payload);

      setMessages((p) => [
        ...p,
        {
          id:      Date.now() + 1,
          from:    "bot",
          text:    data.formatted_text,
          results: data.results || [],
        },
      ]);
    } catch (err) {
      setMessages((p) => [
        ...p,
        {
          id:      Date.now() + 1,
          from:    "bot",
          text:    `Sorry, I hit an error: ${err.message}. Please try again.`,
          results: [],
        },
      ]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex h-[520px] flex-col rounded-2xl border border-slate-700/60 bg-slate-900/70 backdrop-blur-sm">
      {/* Header */}
      <div className={`flex items-center gap-2 rounded-t-2xl bg-gradient-to-r ${cfg.accent} px-4 py-3`}>
        <Bot size={18} className="text-white" />
        <h3 className="font-semibold text-white">Nexus AI Assistant</h3>
        <span className="ml-auto rounded-full bg-white/20 px-2 py-0.5 text-xs text-white capitalize">
          {role}
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`${msg.from === "user" ? "flex justify-end" : ""}`}
            >
              <div
                className={`max-w-[88%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  msg.from === "user"
                    ? `bg-gradient-to-r ${cfg.accent} text-white`
                    : "bg-slate-800 text-slate-100"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.text}</p>
                {msg.results?.map((r, i) => <MatchCard key={i} result={r} />)}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {busy && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-2 text-slate-400 text-sm">
            <Loader2 size={14} className="animate-spin" />
            Analysing matches…
          </motion.div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <form onSubmit={send} className="flex gap-2 border-t border-slate-800 p-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={cfg.placeholder}
          disabled={busy}
          className="flex-1 rounded-xl border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm outline-none focus:border-violet-500 transition-colors disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          className={`rounded-xl bg-gradient-to-r ${cfg.accent} px-3 py-2 text-white transition-opacity hover:opacity-90 disabled:opacity-40`}
        >
          <SendHorizonal size={16} />
        </button>
      </form>
    </div>
  );
}
