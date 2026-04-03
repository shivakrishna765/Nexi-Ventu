import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import DashboardCards from "../components/DashboardCards";
import Chatbot from "../components/Chatbot";
import Card from "../components/Card";
import Skeleton from "../components/Skeleton";
import { startupData } from "../data/mock";

export default function Dashboard() {
  const [params] = useSearchParams();
  const role = params.get("role") || "investor";
  const [loading] = useState(false);

  const heading = useMemo(() => {
    const map = {
      investor: "Investor Dashboard",
      founder: "Founder Dashboard",
      "team seeker": "Team Seeker Dashboard",
      collaborator: "Collaborator Dashboard"
    };
    return map[role] || "Nexus Dashboard";
  }, [role]);

  return (
    <main className="section-wrap grid gap-5 py-8 md:grid-cols-[220px_1fr]">
      <Sidebar />
      <section className="space-y-5">
        <h1 className="text-2xl font-semibold">{heading}</h1>
        {loading ? (
          <div className="grid gap-4 md:grid-cols-3">
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </div>
        ) : (
          <DashboardCards role={role} />
        )}
        <div className="grid gap-4 lg:grid-cols-[1fr_380px]">
          <Card>
            <h2 className="mb-3 text-lg font-semibold">Recommended Opportunities</h2>
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
