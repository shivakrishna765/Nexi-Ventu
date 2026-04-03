import { useMemo } from "react";
import Sidebar from "../components/Sidebar";
import Card from "../components/Card";
import Chatbot from "../components/Chatbot";
import { startupData } from "../data/mock";

const contentByRole = {
  investor: {
    title: "Investor Workspace",
    kpis: ["Deal Flow Quality", "Portfolio Match Index", "Funding Pipeline"],
    panelTitle: "Recommended startups for investment"
  },
  founder: {
    title: "Founder Workspace",
    kpis: ["Team Completion", "Investor Interest", "Product Momentum"],
    panelTitle: "Team suggestions and investor opportunities"
  },
  "team seeker": {
    title: "Team Seeker Workspace",
    kpis: ["Opportunity Match", "Skill Relevance", "Interview Readiness"],
    panelTitle: "Startups hiring for your skill profile"
  },
  collaborator: {
    title: "Collaborator Workspace",
    kpis: ["Co-Founder Compatibility", "Network Strength", "Partnership Readiness"],
    panelTitle: "Potential co-founders and collaboration paths"
  }
};

export default function RoleWorkspace({ role = "investor" }) {
  const data = useMemo(() => contentByRole[role] || contentByRole.investor, [role]);

  return (
    <main className="section-wrap grid gap-5 py-8 md:grid-cols-[220px_1fr]">
      <Sidebar role={role} />
      <section className="space-y-5">
        <h1 className="text-2xl font-semibold">{data.title}</h1>
        <div className="grid gap-4 md:grid-cols-3">
          {data.kpis.map((kpi) => (
            <Card key={kpi}>
              <p className="text-xs uppercase text-slate-400">Live KPI</p>
              <h2 className="mt-2 text-lg font-semibold">{kpi}</h2>
              <p className="mt-2 text-sm text-slate-300">Updated from profile behavior and recommendation interactions.</p>
            </Card>
          ))}
        </div>

        <div className="grid gap-4 lg:grid-cols-[1fr_380px]">
          <Card>
            <h2 className="mb-3 text-lg font-semibold">{data.panelTitle}</h2>
            <div className="space-y-3">
              {startupData.map((s) => (
                <div key={s.id} className="rounded-xl border border-slate-700 bg-slate-900/70 p-3">
                  <div className="flex items-center justify-between">
                    <p className="font-medium">{s.name}</p>
                    <span className="rounded-full bg-indigo-500/25 px-2 py-1 text-xs">{s.match}% Match</span>
                  </div>
                  <p className="text-sm text-slate-300">{s.description}</p>
                  <p className="mt-1 text-xs text-cyan-300">Why this match: {s.why}</p>
                </div>
              ))}
            </div>
          </Card>
          <Chatbot />
        </div>
      </section>
    </main>
  );
}
