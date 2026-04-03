import { Rocket, User, MessageCircleMore, BriefcaseBusiness } from "lucide-react";
import { NavLink } from "react-router-dom";
import { roleToRoute } from "../utils/session";

export default function Sidebar({ role = "investor" }) {
  const workspaceRoute = roleToRoute(role);
  const items = [
    { to: workspaceRoute, icon: BriefcaseBusiness, label: "My Workspace" },
    { to: "/startups", icon: Rocket, label: "Startup Listing" },
    { to: "/profile", icon: User, label: "My Profile" },
    { to: workspaceRoute, icon: MessageCircleMore, label: "AI Assistant" }
  ];
  return (
    <aside className="glass h-fit rounded-2xl p-3">
      {items.map((item) => (
        <NavLink
          key={item.label}
          to={item.to}
          className={({ isActive }) =>
            `mb-1 flex items-center gap-3 rounded-xl px-3 py-2 text-sm transition ${
              isActive ? "bg-slate-800 text-white" : "text-slate-300 hover:bg-slate-800/70"
            }`
          }
        >
          <item.icon size={16} />
          {item.label}
        </NavLink>
      ))}
    </aside>
  );
}
