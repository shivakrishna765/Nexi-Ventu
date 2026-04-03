import { Link, NavLink, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { LogOut, User, LayoutDashboard } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { roleToRoute } from "../utils/session";
import NotificationBell from "./NotificationBell";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const dashRoute = user ? roleToRoute(user.role) : "/login";

  const links = [
    { to: "/", label: "Home" },
    ...(user ? [{ to: dashRoute, label: "Dashboard" }] : []),
    ...(user ? [{ to: "/startups", label: "Startups" }] : []),
  ];

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="sticky top-0 z-50 border-b border-slate-800/60 bg-black/30 backdrop-blur-xl"
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 md:px-8">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 text-lg font-bold tracking-tight">
          <span className="rounded-lg bg-gradient-to-br from-violet-600 to-cyan-500 p-1.5 text-xs font-black text-white">NV</span>
          Nexus <span className="text-cyan-400">Venture</span>
        </Link>

        {/* Nav links */}
        <nav className="hidden items-center gap-6 md:flex">
          {links.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `text-sm transition-colors ${isActive ? "text-white" : "text-slate-400 hover:text-white"}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {user ? (
            <>
              <NotificationBell />
              <Link
                to="/profile"
                className="flex items-center gap-2 rounded-xl border border-slate-700 px-3 py-1.5 text-sm hover:bg-slate-800/60 transition-colors"
              >
                <User size={14} />
                <span className="hidden sm:inline">{user.name?.split(" ")[0]}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 rounded-xl border border-slate-700 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-800/60 hover:text-white transition-colors"
              >
                <LogOut size={14} />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="rounded-xl bg-gradient-to-r from-violet-600 to-cyan-500 px-4 py-1.5 text-sm font-medium text-white hover:opacity-90 transition-opacity"
            >
              Get Started
            </Link>
          )}
        </div>
      </div>
    </motion.header>
  );
}
