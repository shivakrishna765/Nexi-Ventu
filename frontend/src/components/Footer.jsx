import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="border-t border-slate-800/60 bg-black/20 py-8 text-sm text-slate-500">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-4 md:flex-row md:px-8">
        <p className="font-semibold text-slate-400">
          Nexus <span className="text-cyan-400">Venture</span>
        </p>
        <p>© {new Date().getFullYear()} Nexus Venture. All rights reserved.</p>
        <div className="flex gap-4">
          <Link to="/" className="hover:text-white transition-colors">Home</Link>
          <Link to="/startups" className="hover:text-white transition-colors">Startups</Link>
          <Link to="/profile" className="hover:text-white transition-colors">Profile</Link>
        </div>
      </div>
    </footer>
  );
}
