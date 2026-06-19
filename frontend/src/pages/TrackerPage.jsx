import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Download, LayoutGrid, List, Mail, ExternalLink, ChevronDown } from "lucide-react";
import api from "../services/api";
import toast from "react-hot-toast";

const STATUSES = [
  { id: "saved", label: "Saved", color: "bg-slate-500/20 text-slate-300 border-slate-500/30" },
  { id: "applied", label: "Applied", color: "bg-blue-500/20 text-blue-300 border-blue-500/30" },
  { id: "shortlisted", label: "Shortlisted", color: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30" },
  { id: "interview", label: "Interview", color: "bg-green-500/20 text-green-300 border-green-500/30" },
  { id: "offer", label: "Offer 🎉", color: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" },
  { id: "rejected", label: "Rejected", color: "bg-red-500/20 text-red-300 border-red-500/30" },
  { id: "ghosted", label: "Ghosted", color: "bg-slate-600/20 text-slate-400 border-slate-600/30" },
  { id: "withdrawn", label: "Withdrawn", color: "bg-orange-500/20 text-orange-300 border-orange-500/30" },
];

function StatusDropdown({ currentStatus, applicationId, onChange }) {
  const [open, setOpen] = useState(false);
  const current = STATUSES.find(s => s.id === currentStatus) || STATUSES[1];

  const handleChange = async (statusId) => {
    setOpen(false);
    try {
      await api.patch(`/applications/${applicationId}/status`, { status: statusId });
      onChange(statusId);
      toast.success("Status updated");
    } catch {
      toast.error("Failed to update status");
    }
  };

  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)}
        className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${current.color}`}>
        {current.label} <ChevronDown size={10} />
      </button>
      {open && (
        <div className="absolute top-full left-0 mt-1 bg-slate-800 border border-slate-700 rounded-xl overflow-hidden z-20 min-w-[140px] shadow-xl">
          {STATUSES.map(s => (
            <button key={s.id} onClick={() => handleChange(s.id)}
              className={`w-full text-left px-3 py-2 text-xs hover:bg-slate-700 transition-colors ${s.id === currentStatus ? "bg-slate-700/50" : ""}`}>
              <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border ${s.color}`}>{s.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function TrackerPage() {
  const [applications, setApplications] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState("table");
  const [exporting, setExporting] = useState(false);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [appsRes, statsRes] = await Promise.all([
        api.get("/applications"),
        api.get("/applications/stats"),
      ]);
      setApplications(appsRes.data.applications);
      setStats(statsRes.data);
    } catch {
      toast.error("Failed to load applications");
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = (appId, newStatus) => {
    setApplications(apps => apps.map(a => a.id === appId ? { ...a, status: newStatus } : a));
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const res = await api.get("/applications/export/excel", { responseType: "blob" });
      const url = URL.createObjectURL(res.data);
      const a = document.createElement("a");
      a.href = url;
      a.download = "firstjob_applications.xlsx";
      a.click();
      toast.success("Excel file downloaded!");
    } catch {
      toast.error("Export failed");
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="bg-slate-950 overflow-y-auto" style={{ height: "calc(100vh - 64px)" }}>
      <div className="max-w-5xl mx-auto p-4 pb-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-white font-semibold text-xl">Application Tracker</h1>
            <p className="text-slate-400 text-sm">{stats?.total || 0} applications tracked</p>
          </div>
          <div className="flex gap-2">
            <div className="flex bg-slate-800 border border-slate-700 rounded-xl p-1">
              <button onClick={() => setView("table")}
                className={`p-1.5 rounded-lg transition-all ${view === "table" ? "bg-indigo-600 text-white" : "text-slate-400"}`}>
                <List size={16} />
              </button>
              <button onClick={() => setView("kanban")}
                className={`p-1.5 rounded-lg transition-all ${view === "kanban" ? "bg-indigo-600 text-white" : "text-slate-400"}`}>
                <LayoutGrid size={16} />
              </button>
            </div>
            <button onClick={handleExport} disabled={exporting}
              className="flex items-center gap-2 px-3 py-2 bg-slate-800 border border-slate-700 text-slate-300 hover:text-white rounded-xl text-sm transition-all">
              <Download size={15} /> {exporting ? "Exporting..." : "Export Excel"}
            </button>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
            {[
              { label: "Total Applied", value: stats.total, color: "text-white" },
              { label: "Response Rate", value: `${stats.response_rate}%`, color: "text-green-400" },
              { label: "Interviews", value: stats.interviews, color: "text-yellow-400" },
              { label: "Offers", value: stats.offers, color: "text-emerald-400" },
            ].map((stat, i) => (
              <div key={i} className="bg-slate-800/50 border border-slate-700 rounded-xl p-3 text-center">
                <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
                <p className="text-xs text-slate-400 mt-0.5">{stat.label}</p>
              </div>
            ))}
          </div>
        )}

        {/* Table view */}
        {view === "table" && (
          <div className="bg-slate-800/50 border border-slate-700 rounded-2xl overflow-hidden">
            {loading ? (
              <div className="py-12 text-center text-slate-400">Loading...</div>
            ) : applications.length === 0 ? (
              <div className="py-12 text-center">
                <p className="text-slate-400">No applications yet</p>
                <p className="text-slate-500 text-sm mt-1">Start swiping on jobs to apply!</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-700">
                      {["Job", "Company", "Location", "Type", "Status", "Applied", "Match", "Outreach", ""].map((h, i) => (
                        <th key={i} className="text-left text-xs text-slate-400 font-medium px-4 py-3">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {applications.map((app, i) => (
                      <motion.tr key={app.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                        transition={{ delay: i * 0.03 }}
                        className="border-b border-slate-700/50 hover:bg-slate-700/20 transition-colors">
                        <td className="px-4 py-3">
                          <p className="text-white font-medium text-xs">{app.job?.title}</p>
                        </td>
                        <td className="px-4 py-3 text-slate-300 text-xs">{app.job?.company}</td>
                        <td className="px-4 py-3 text-slate-400 text-xs">{app.job?.location || "—"}</td>
                        <td className="px-4 py-3 text-slate-400 text-xs">{app.job?.job_type?.replace("_", " ") || "—"}</td>
                        <td className="px-4 py-3">
                          <StatusDropdown currentStatus={app.status} applicationId={app.id}
                            onChange={(s) => handleStatusChange(app.id, s)} />
                        </td>
                        <td className="px-4 py-3 text-slate-400 text-xs">
                          {app.applied_at ? new Date(app.applied_at).toLocaleDateString("en-IN", { day: "numeric", month: "short" }) : "—"}
                        </td>
                        <td className="px-4 py-3 text-xs">
                          {app.job?.match_score ? (
                            <span className={app.job.match_score >= 70 ? "text-green-400" : "text-yellow-400"}>
                              {app.job.match_score.toFixed(0)}%
                            </span>
                          ) : "—"}
                        </td>
                        <td className="px-4 py-3">
                          {app.outreach?.length > 0 ? (
                            <span className="flex items-center gap-1 text-xs text-indigo-300">
                              <Mail size={11} /> {app.outreach[0].status}
                            </span>
                          ) : <span className="text-xs text-slate-500">—</span>}
                        </td>
                        <td className="px-4 py-3">
                          {app.job?.source_url && (
                            <a href={app.job.source_url} target="_blank" rel="noopener noreferrer"
                              className="text-slate-500 hover:text-indigo-400 transition-colors">
                              <ExternalLink size={13} />
                            </a>
                          )}
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Kanban view */}
        {view === "kanban" && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {["applied", "shortlisted", "interview", "offer", "rejected", "ghosted"].map(status => {
              const statusInfo = STATUSES.find(s => s.id === status);
              const statusApps = applications.filter(a => a.status === status);
              return (
                <div key={status} className="bg-slate-800/50 border border-slate-700 rounded-xl p-3">
                  <div className="flex items-center justify-between mb-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${statusInfo?.color}`}>{statusInfo?.label}</span>
                    <span className="text-xs text-slate-500">{statusApps.length}</span>
                  </div>
                  <div className="space-y-2">
                    {statusApps.map(app => (
                      <div key={app.id} className="bg-slate-700/50 rounded-lg p-2.5">
                        <p className="text-white text-xs font-medium leading-tight">{app.job?.title}</p>
                        <p className="text-slate-400 text-xs mt-0.5">{app.job?.company}</p>
                      </div>
                    ))}
                    {statusApps.length === 0 && <p className="text-slate-600 text-xs text-center py-2">None yet</p>}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
