import Card from "./Card";

export default function DashboardCards({ role }) {
  const roleWidgets = {
    investor: ["Recommended Startups", "Funding Pipeline", "Risk Insights"],
    founder: ["Team Suggestions", "Investor Matches", "Startup Growth Tracker"],
    "team seeker": ["Open Opportunities", "Skill Match Index", "Interview Activity"],
    collaborator: ["Co-Founder Matches", "Networking Suggestions", "Partnership Tracker"]
  };

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {(roleWidgets[role] || roleWidgets.investor).map((item, idx) => (
        <Card key={item}>
          <p className="text-xs uppercase text-slate-400">Module {idx + 1}</p>
          <h3 className="mt-2 text-lg font-semibold">{item}</h3>
          <p className="mt-2 text-sm text-slate-300">Live analytics and AI-driven insights for this section.</p>
        </Card>
      ))}
    </div>
  );
}
