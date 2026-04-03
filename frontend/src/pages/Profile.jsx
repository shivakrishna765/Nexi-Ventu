import { useState } from "react";
import { motion } from "framer-motion";
import { Save, User } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const ROLES = ["investor", "founder", "seeker", "collaborator"];
const LEVELS = ["junior", "mid", "senior"];
const STAGES = ["Pre-Seed", "Seed", "Series A", "Series B", "Series C"];

export default function Profile() {
  const { user, updateUser } = useAuth();
  const [form, setForm] = useState({
    name:                    user?.name                    || "",
    role:                    user?.role                    || "seeker",
    skills:                  user?.skills                  || user?.bio || "",
    interests:               user?.interests               || "",
    experience_level:        user?.experience_level        || "",
    location:                user?.location                || "",
    preferred_funding_stage: user?.preferred_funding_stage || "",
    bio:                     user?.bio                     || "",
  });
  const [saving, setSaving]   = useState(false);
  const [saved, setSaved]     = useState(false);
  const [error, setError]     = useState("");

  const update = (key, val) => setForm((p) => ({ ...p, [key]: val }));

  const save = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      await updateUser(form);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      setError(err.message || "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 md:px-8">
      <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }}>
        {/* Avatar */}
        <div className="mb-6 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-cyan-500 text-2xl font-bold text-white">
            {user?.name?.[0] || <User size={24} />}
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">{user?.name}</h1>
            <p className="text-sm text-slate-400 capitalize">{user?.email}</p>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-700/60 bg-slate-900/70 p-6 backdrop-blur-sm">
          <h2 className="mb-5 font-semibold text-white">Edit Profile</h2>
          <form onSubmit={save} className="space-y-4">
            <Field label="Full Name">
              <input value={form.name} onChange={(e) => update("name", e.target.value)}
                className="input-field" placeholder="Your full name" />
            </Field>

            <Field label="Role">
              <select value={form.role} onChange={(e) => update("role", e.target.value)} className="input-field capitalize">
                {ROLES.map((r) => <option key={r} value={r} className="capitalize">{r}</option>)}
              </select>
            </Field>

            <Field label="Skills" hint="Comma-separated, e.g. Python, React, ML">
              <input value={form.skills} onChange={(e) => update("skills", e.target.value)}
                className="input-field" placeholder="Python, React, Machine Learning…" />
            </Field>

            <Field label="Domain Interests" hint="e.g. AI, Healthcare, Fintech">
              <input value={form.interests} onChange={(e) => update("interests", e.target.value)}
                className="input-field" placeholder="AI, Healthcare, Fintech…" />
            </Field>

            <div className="grid gap-4 sm:grid-cols-2">
              <Field label="Experience Level">
                <select value={form.experience_level} onChange={(e) => update("experience_level", e.target.value)} className="input-field capitalize">
                  <option value="">Select level</option>
                  {LEVELS.map((l) => <option key={l} value={l} className="capitalize">{l}</option>)}
                </select>
              </Field>
              <Field label="Location">
                <input value={form.location} onChange={(e) => update("location", e.target.value)}
                  className="input-field" placeholder="City, e.g. Bangalore" />
              </Field>
            </div>

            <Field label="Preferred Funding Stage">
              <select value={form.preferred_funding_stage} onChange={(e) => update("preferred_funding_stage", e.target.value)} className="input-field">
                <option value="">Any stage</option>
                {STAGES.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </Field>

            <Field label="Bio">
              <textarea value={form.bio} onChange={(e) => update("bio", e.target.value)}
                rows={3} className="input-field resize-none" placeholder="Brief description of your background…" />
            </Field>

            {error && (
              <p className="rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-400">{error}</p>
            )}

            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 px-5 py-2.5 font-medium text-white hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              <Save size={15} />
              {saving ? "Saving…" : saved ? "Saved ✓" : "Save Changes"}
            </button>
          </form>
        </div>
      </motion.div>

      <style>{`.input-field { width: 100%; border-radius: 0.75rem; border: 1px solid rgb(51 65 85 / 0.8); background: rgb(2 6 23 / 0.6); padding: 0.625rem 1rem; font-size: 0.875rem; color: white; outline: none; transition: border-color 0.15s; } .input-field:focus { border-color: rgb(139 92 246); }`}</style>
    </div>
  );
}

function Field({ label, hint, children }) {
  return (
    <div>
      <label className="mb-1.5 block text-xs font-medium uppercase tracking-wide text-slate-400">
        {label} {hint && <span className="normal-case text-slate-600">— {hint}</span>}
      </label>
      {children}
    </div>
  );
}
