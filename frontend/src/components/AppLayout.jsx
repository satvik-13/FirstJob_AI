import { NavLink, Outlet } from "react-router-dom";
import { Briefcase, LayoutDashboard, User, Mail } from "lucide-react";

const NAV_ITEMS = [
  { to: "/jobs", icon: Briefcase, label: "Jobs" },
  { to: "/tracker", icon: LayoutDashboard, label: "Tracker" },
  { to: "/outreach", icon: Mail, label: "Outreach" },
  { to: "/profile", icon: User, label: "Profile" },
];

export default function AppLayout() {
  return (
    <div className="flex flex-col h-screen bg-slate-950 overflow-hidden">
      {/* Page content - exactly viewport minus nav */}
      <div className="flex-1 overflow-hidden">
        <Outlet />
      </div>

      {/* Bottom nav - fixed 64px height */}
      <nav className="h-16 bg-slate-900 border-t border-slate-800 flex items-center justify-around px-2 flex-shrink-0">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to}
            className={({ isActive }) =>
              `flex flex-col items-center gap-0.5 px-4 py-2 rounded-xl transition-all
              ${isActive ? "text-indigo-400" : "text-slate-500 hover:text-slate-300"}`
            }>
            <Icon size={20} />
            <span className="text-xs">{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
