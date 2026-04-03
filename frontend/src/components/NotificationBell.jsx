import { Bell } from "lucide-react";
import { notifications } from "../data/mock";

export default function NotificationBell() {
  return (
    <div className="group relative">
      <button className="rounded-lg border border-slate-700 p-2 text-slate-300 hover:bg-slate-800">
        <Bell size={16} />
      </button>
      <div className="invisible absolute right-0 mt-2 w-72 rounded-xl border border-slate-700 bg-slate-900 p-3 text-sm opacity-0 shadow-card transition group-hover:visible group-hover:opacity-100">
        <p className="mb-2 text-xs uppercase text-slate-400">Notifications</p>
        {notifications.map((n) => (
          <p key={n} className="mb-2 border-b border-slate-800 pb-2 text-slate-200">
            {n}
          </p>
        ))}
      </div>
    </div>
  );
}
