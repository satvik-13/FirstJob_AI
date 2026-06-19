import { useEffect, useState } from "react";
import { Mail, CheckCircle, Clock, AlertCircle, Send, RefreshCw } from "lucide-react";
import api from "../services/api";
import toast from "react-hot-toast";

const STATUS_CONFIG = {
  sent:    { icon: Send, color: "text-blue-400", label: "Sent" },
  opened:  { icon: CheckCircle, color: "text-green-400", label: "Opened" },
  replied: { icon: CheckCircle, color: "text-emerald-400", label: "Replied ✓" },
  pending: { icon: Clock, color: "text-yellow-400", label: "Pending" },
  failed:  { icon: AlertCircle, color: "text-red-400", label: "Failed" },
  bounced: { icon: AlertCircle, color: "text-orange-400", label: "Bounced" },
};

export default function OutreachPage() {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get("/applications")
      .then(res => setApplications(res.data.applications.filter(a => a.outreach?.length > 0)))
      .catch(() => toast.error("Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  const allOutreaches = applications.flatMap(app =>
    app.outreach.map(o => ({ ...o, job: app.job }))
  );

  const stats = {
    total: allOutreaches.length,
    sent: allOutreaches.filter(o => o.status === "sent" || o.status === "opened" || o.status === "replied").length,
    replied: allOutreaches.filter(o => o.status === "replied").length,
    followups: allOutreaches.filter(o => o.followup_sent).length,
  };

  return (
    <div className="bg-slate-950 overflow-y-auto" style={{ height: "calc(100vh - 64px)" }}>
      <div className="max-w-2xl mx-auto p-4 pb-8">
        <div className="mb-4">
          <h1 className="text-white font-semibold text-xl flex items-center gap-2">
            <Mail size={20} className="text-indigo-400" /> Cold Outreach
          </h1>
          <p className="text-slate-400 text-sm">{stats.total} emails sent to hiring managers</p>
        </div>

        {/* Stats */}
        {stats.total > 0 && (
          <div className="grid grid-cols-3 gap-3 mb-4">
            {[
              { label: "Emails Sent", value: stats.sent, color: "text-blue-400" },
              { label: "Replied", value: stats.replied, color: "text-emerald-400" },
              { label: "Follow-ups", value: stats.followups, color: "text-yellow-400" },
            ].map((s, i) => (
              <div key={i} className="bg-slate-800/50 border border-slate-700 rounded-xl p-3 text-center">
                <p className={`text-xl font-bold ${s.color}`}>{s.value}</p>
                <p className="text-xs text-slate-400 mt-0.5">{s.label}</p>
              </div>
            ))}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12 text-slate-400 flex flex-col items-center gap-3">
            <RefreshCw size={24} className="animate-spin" />
            <p>Loading outreach data...</p>
          </div>
        ) : allOutreaches.length === 0 ? (
          <div className="text-center py-12">
            <Mail size={40} className="text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400 font-medium">No outreach emails sent yet</p>
            <p className="text-slate-500 text-sm mt-1">Apply to jobs and cold emails will be sent automatically to HRs</p>
          </div>
        ) : (
          <div className="space-y-3">
            {allOutreaches.map((o, i) => {
              const statusConfig = STATUS_CONFIG[o.status] || STATUS_CONFIG.sent;
              const StatusIcon = statusConfig.icon;
              return (
                <div key={o.id || i} className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-white font-medium text-sm truncate">{o.subject}</p>
                      <p className="text-slate-400 text-xs mt-0.5">
                        To: <span className="text-slate-300">{o.contact_name || "HR"}</span>
                        {o.contact_role && <span className="text-slate-500"> · {o.contact_role}</span>}
                        <span className="text-slate-500"> at {o.job?.company}</span>
                      </p>
                      <p className="text-slate-500 text-xs">{o.contact_email}</p>
                    </div>
                    <div className={`flex items-center gap-1.5 text-xs flex-shrink-0 ${statusConfig.color}`}>
                      <StatusIcon size={13} />
                      <span>{statusConfig.label}</span>
                    </div>
                  </div>

                  {/* Email preview */}
                  <div className="bg-slate-700/30 rounded-lg p-3 mt-2">
                    <p className="text-slate-300 text-xs leading-relaxed line-clamp-3">{o.body}</p>
                  </div>

                  <div className="flex items-center justify-between mt-2">
                    {o.sent_at && (
                      <p className="text-slate-600 text-xs">
                        Sent {new Date(o.sent_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })}
                      </p>
                    )}
                    {o.followup_sent && (
                      <span className="text-xs text-yellow-400 bg-yellow-500/10 px-2 py-0.5 rounded-full">Follow-up sent</span>
                    )}
                    {!o.followup_sent && o.followup_scheduled_at && (
                      <span className="text-xs text-slate-500">
                        Follow-up in 4 days
                      </span>
                    )}
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
