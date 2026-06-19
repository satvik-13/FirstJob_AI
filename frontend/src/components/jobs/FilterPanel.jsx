import { motion } from "framer-motion";
import { X } from "lucide-react";
import { useState } from "react";
import useJobsStore from "../../store/jobsStore";

const JOB_TYPES = [
  { id: "full_time", label: "Full-time" },
  { id: "internship", label: "Internship" },
  { id: "remote", label: "Remote" },
  { id: "hybrid", label: "Hybrid" },
  { id: "contract", label: "Contract" },
];

const SORT_OPTIONS = [
  { id: "match_score", label: "Best match" },
  { id: "recent", label: "Most recent" },
  { id: "salary", label: "Highest salary" },
];

export default function FilterPanel({ onClose }) {
  const { filters, setFilters } = useJobsStore();
  const [local, setLocal] = useState({ ...filters });

  const handleApply = () => {
    setFilters(local);
    onClose();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="mx-4 mb-3 bg-slate-800 border border-slate-700 rounded-2xl p-4 space-y-4"
    >
      <div className="flex items-center justify-between">
        <p className="text-white font-medium text-sm">Filter Jobs</p>
        <button onClick={onClose} className="text-slate-500 hover:text-white"><X size={16} /></button>
      </div>

      {/* Job type */}
      <div>
        <p className="text-xs text-slate-400 mb-2">Job type</p>
        <div className="flex flex-wrap gap-2">
          {JOB_TYPES.map(t => (
            <button key={t.id}
              onClick={() => setLocal(l => ({ ...l, job_type: l.job_type === t.id ? "" : t.id }))}
              className={`text-xs px-3 py-1.5 rounded-full border transition-all
                ${local.job_type === t.id
                  ? "bg-indigo-600/30 border-indigo-500 text-indigo-200"
                  : "border-slate-600 text-slate-400 hover:border-slate-500"}`}>
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* Location */}
      <div>
        <p className="text-xs text-slate-400 mb-2">Location</p>
        <input value={local.location || ""}
          onChange={e => setLocal(l => ({ ...l, location: e.target.value }))}
          placeholder="e.g. Bangalore, Mumbai, Remote"
          className="w-full bg-slate-700/50 border border-slate-600 text-white placeholder-slate-500 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-indigo-500" />
      </div>

      {/* Sort */}
      <div>
        <p className="text-xs text-slate-400 mb-2">Sort by</p>
        <div className="flex gap-2">
          {SORT_OPTIONS.map(s => (
            <button key={s.id}
              onClick={() => setLocal(l => ({ ...l, sort_by: s.id }))}
              className={`text-xs px-3 py-1.5 rounded-full border transition-all
                ${local.sort_by === s.id
                  ? "bg-indigo-600/30 border-indigo-500 text-indigo-200"
                  : "border-slate-600 text-slate-400"}`}>
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <button onClick={handleApply}
        className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-xl">
        Apply filters
      </button>
    </motion.div>
  );
}
