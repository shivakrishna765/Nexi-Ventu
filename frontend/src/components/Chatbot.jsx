import { useState, useRef, useEffect } from "react";
import { SendHorizonal, Bot, Loader2, RefreshCw } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../context/AuthContext";
import { api } from "../utils/api";

const ROLE_CONFIG = {
  investor: {
    greeting: (name) => `Hi ${name}! I'm your Nexus investment advisor. Ask me about startups, domains, funding stages, or locations.`,
    placeholder: "e.g. Show me AI startups at seed stage in Bangalore…",
    accent: "from-amber-500 to-yellow-400",
    suggestions: ["Find AI healthcare startups", "Seed stage fintech companies", "High-growth startups in Mumbai"],
  },
  founder: {
    greeting: (name) => `Welcome ${name}! I'll help you find team members, investors, and co-founders. What are you building?`,
    placeholder: "e.g. Need ML engineers for my healthtech startup…",
    accent: "from-violet-500 to-indigo-400",
    suggestions: ["Find Python ML engineers", "Investors for seed stage AI startup", "Co-founders with React skills"],
  },
  seeker: {
    greeting: (name) => `Hey ${name}! Tell me your skills and I'll match you with startups hiring right now.`,
    placeholder: "e.g. Python developer interested in healthtech…",
    accent: "from-emerald-500 to-cyan-400",
    suggestions: ["Startups needing Python developers", "AI companies hiring juniors", "Remote fintech opportunities"],
  },
  member: {
    greeting: (name) => `Hey ${name}! Tell me your skills and I'll match you with startups hiring right now.`,
    placeholder: "e.g. Python developer interested in healthtech…",
    accent: "from-emerald-500 to-cyan-400",
    suggestions: ["Startups needing Python developers", "AI companies hiring", "Fintech opportunities"],
  },
  collaborator: {
    greeting: (name) => `Hi ${name}! I'll find co-founders and partners that match your vision. What's your domain?`,
    placeholder: "e.g. Full-stack dev looking for a fintech co-founder…",
    accent: "from-pink-500 to-rose-400",
    suggestions: ["Find fintech co-founders", "Blockchain startup partners", "EdTech collaboration opportunities"],
  },
};

function MatchCard({ result }) {
  return (
    <div className="mt-2 rounded-xl border border-slate-700/60 bg-slate-800/60 p-3 text-xs">
      <div className="flex items-center justify-between gap-2">
        <span className="font-semibold text-white truncate">{result.name}</span>
        <span className="shrink-0 rounded-full bg-violet-500/25 px-2 py-0.5 text-violet-300">
          {result.match_score}%
        </span>
      </div>
      {result.domain && <p className="mt-1 text-slate-400">📌 {result.domain}</p>}
      {result.funding_stage && <p className="text-slate-400">💰 {result.funding_stage}</p>}
      {result.location && <p className="text-slate-400">📍 {result.location}</p>}
      {result.reasons?.slice(0, 2).map((r, i) => (
        <p key={i} className="mt-1 text-cyan-400/80">• {r}</p>
      ))}
    </div>
  );
}

export default function Chatbot({ role: propRole }) {
  const { user } = useAuth();
  const role    = propRole || user?.role || "seeker";
  const cfg     = ROLE_CONFIG[role] || ROLE_CONFIG.seeker;
  const firstName = user?.name?.split(" ")[0] || "there";

  const [messages, setMessages] = useState([
    { id: 0, from: "bot", text: cfg.greeting(firstName), results: [] },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy]   = useState(false);
  const bottomRef         = useRef(null);

  // Reset when role changes
  useEffect(() => {
    setMessages([{ id: 0, from: "bot", text: cfg.greeting(firstName), results: [] }]);
    setInput("");
  }, [role]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text) => {
    if (!text.trim() || busy) return;

    const userMsg = { id: Date.now(), from: "user", text: text.trim(), results: [] };
    setMessages((p) => [...p, userMsg]);
    setInput("");
    setBusy(true);

    try {
      // Build conversation history from last 4 exchanges for memory
      const history = messages
        .filter((m) => m.from !== "bot" || m.id !== 0) // skip greeting
        .slice(-8)
        .map((m) => `${m.from === "user" ? "User" : "Assistant"}: ${m.text.slice(0, 200)}`)
        .join("\n");

      const payload = {
        query:    text.trim(),
        role:     role,
        // Merge stored profile with any inline context
        skills:   [user?.skills, user?.bio].filter(Boolean).join(" ") || "",
        interests: user?.interests || "",
        location:  user?.location  || "",
        top_n:    5,
        memory_turns: 4,
        use_ai_style: true,
        // Pass history as part of query context so backend can use it
        ...(history ? { _history_hint: history } : {}),
      };

      const data = user
        ? await api.chat(payload)
        : await api.chatDemo({ ...payload, role });

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
          id:   Date.now() + 1,
          from: "bot",
          text: `Something went wrong: ${err.message}`,
          results: [],
        },
      ]);
    } finally {
      setBusy(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const clearChat = () => {
    setMessages([{ id: Date.now(), from: "bot", text: cfg.greeting(firstName), results: [] }]);
    setInput("");
  };

  return (
    <div className="flex h-[540px] flex-col rounded-2xl border border-slate-700/60 bg-slate-900/70 backdrop-blur-sm">
      {/* Header */}
      <div className={`flex items-center gap-2 rounded-t-2xl bg-gradient-to-r ${cfg.accent} px-4 py-3`}>
        <Bot size={18} className="text-white" />
        <h3 className="font-semibold text-white">Nexus AI</h3>
        <span className="ml-auto rounded-full bg-white/20 px-2 py-0.5 text-xs text-white capitalize">{role}</span>
        <button
          onClick={clearChat}
          title="Clear chat"
          className="ml-1 rounded-lg p-1 text-white/70 hover:bg-white/20 hover:text-white transition-colors"
        >
          <RefreshCw size={13} />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        <AnimatePresence initial={false}>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.18 }}
              className={msg.from === "user" ? "flex justify-end" : ""}
            >
              <div
                className={`max-w-[90%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
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
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2 text-slate-400 text-xs"
          >
            <Loader2 size={13} className="animate-spin" />
            Analysing…
          </motion.div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Quick suggestions — only show when chat is fresh */}
      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-1.5 px-4 pb-2">
          {cfg.suggestions.map((s) => (
            <button
              key={s}
              onClick={() => sendMessage(s)}
              className="rounded-full border border-slate-700 bg-slate-800/60 px-2.5 py-1 text-xs text-slate-300 hover:border-slate-500 hover:text-white transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="flex gap-2 border-t border-slate-800 p-3">
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
