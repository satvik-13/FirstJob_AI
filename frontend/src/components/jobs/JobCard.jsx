import { motion, useMotionValue, useTransform, useAnimation } from "framer-motion";
import { useState } from "react";
import { MapPin, Briefcase, Star, ExternalLink, X, Check, Building2, ChevronDown, ChevronUp } from "lucide-react";

const SOURCE_LABELS = {
  indeed: { label: "Indeed", color: "bg-blue-500/20 text-blue-300" },
  linkedin: { label: "LinkedIn", color: "bg-sky-500/20 text-sky-300" },
  naukri: { label: "Naukri", color: "bg-orange-500/20 text-orange-300" },
  internshala: { label: "Internshala", color: "bg-green-500/20 text-green-300" },
  glassdoor: { label: "Glassdoor", color: "bg-emerald-500/20 text-emerald-300" },
};

function MatchBadge({ score }) {
  if (!score) return null;
  const color = score >= 75 ? "text-green-400 border-green-500/30 bg-green-500/10"
    : score >= 50 ? "text-yellow-400 border-yellow-500/30 bg-yellow-500/10"
    : "text-red-400 border-red-500/30 bg-red-500/10";
  return (
    <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full border text-xs font-medium ${color}`}>
      <Star size={10} fill="currentColor" />
      {score.toFixed(0)}% match
    </div>
  );
}

export default function JobCard({ job, onSwipeLeft, onApply, isTop }) {
  const [expanded, setExpanded] = useState(false);
  const [actionState, setActionState] = useState(null);

  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-20, 20]);
  const likeOpacity = useTransform(x, [30, 100], [0, 1]);
  const nopeOpacity = useTransform(x, [-100, -30], [1, 0]);
  const controls = useAnimation();

  const source = SOURCE_LABELS[job.source] || { label: job.source, color: "bg-slate-500/20 text-slate-300" };

  const runApply = async () => {
    setActionState("applying");
    try {
      await onApply?.(job.id);
      await controls.start({ x: 500, opacity: 0 });
    } catch {
      setActionState(null);
      controls.start({ x: 0, rotate: 0 });
    }
  };

  const handleDragEnd = async (_, info) => {
    if (info.offset.x > 100) {
      // Swiping right now applies directly — same as the button.
      await runApply();
    } else if (info.offset.x < -100) {
      await controls.start({ x: -500, opacity: 0 });
      onSwipeLeft?.(job.id);
    } else {
      controls.start({ x: 0, rotate: 0 });
    }
  };

  const handleApplyClick = () => {
    runApply();
  };

  const salaryDisplay = () => {
    if (!job.salary_min && !job.salary_max) return null;
    const curr = job.salary_currency === "INR" ? "₹" : "$";
    const fmt = (n) => n >= 100000 ? `${(n / 100000).toFixed(1)}L` : n >= 1000 ? `${(n / 1000).toFixed(0)}K` : n;
    if (job.salary_min && job.salary_max) return `${curr}${fmt(job.salary_min)} – ${fmt(job.salary_max)}`;
    if (job.salary_min) return `${curr}${fmt(job.salary_min)}+`;
    return null;
  };

  if (!isTop) {
    return <div className="absolute inset-0 rounded-2xl bg-slate-800/40 border border-slate-700/50 scale-95 -z-10" />;
  }

  return (
    <motion.div
      style={{ x, rotate }}
      animate={controls}
      drag={isTop ? "x" : false}
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={handleDragEnd}
      className="absolute inset-0 cursor-grab active:cursor-grabbing select-none"
    >
      {/* Overlays */}
      <motion.div style={{ opacity: likeOpacity }}
        className="absolute top-6 left-6 z-10 rotate-[-15deg] border-4 border-green-400 text-green-400 font-black text-2xl px-3 py-1 rounded-xl pointer-events-none">
        APPLY
      </motion.div>
      <motion.div style={{ opacity: nopeOpacity }}
        className="absolute top-6 right-6 z-10 rotate-[15deg] border-4 border-red-400 text-red-400 font-black text-2xl px-3 py-1 rounded-xl pointer-events-none">
        SKIP
      </motion.div>

      <div className="h-full bg-slate-800 border border-slate-700 rounded-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-br from-indigo-600/20 to-purple-600/20 p-4 border-b border-slate-700 flex-shrink-0">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-3">
              {job.company_logo ? (
                <img src={job.company_logo} alt={job.company} className="w-11 h-11 rounded-xl object-contain bg-white p-1 flex-shrink-0" />
              ) : (
                <div className="w-11 h-11 rounded-xl bg-indigo-500/20 flex items-center justify-center flex-shrink-0">
                  <Building2 size={20} className="text-indigo-400" />
                </div>
              )}
              <div className="min-w-0">
                <h2 className="text-white font-semibold text-sm leading-tight line-clamp-2">{job.title}</h2>
                <p className="text-slate-300 text-xs">{job.company}</p>
              </div>
            </div>
            <MatchBadge score={job.match_score} />
          </div>

          <div className="flex flex-wrap gap-x-3 gap-y-1 mt-2">
            {job.location && (
              <span className="flex items-center gap-1 text-xs text-slate-400">
                <MapPin size={10} /> {job.location}
              </span>
            )}
            {job.job_type && (
              <span className="flex items-center gap-1 text-xs text-slate-400">
                <Briefcase size={10} /> {job.job_type.replace("_", " ")}
              </span>
            )}
            {salaryDisplay() && (
              <span className="text-xs text-green-400 font-medium">{salaryDisplay()}</span>
            )}
            <span className={`text-xs px-2 py-0.5 rounded-full ${source.color}`}>{source.label}</span>
          </div>
        </div>

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {/* Match reasons */}
          {job.match_reasons?.filter(r => !r.includes("compute")).length > 0 && (
            <div>
              <p className="text-xs font-medium text-slate-400 mb-1.5">Why you match</p>
              <div className="space-y-1">
                {job.match_reasons.slice(0, 3).map((r, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs text-slate-300">
                    <Check size={11} className="text-green-400 mt-0.5 flex-shrink-0" /> {r}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Skills */}
          {job.skills_required?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-slate-400 mb-1.5">Skills required</p>
              <div className="flex flex-wrap gap-1.5">
                {job.skills_required.slice(0, 10).map((s, i) => (
                  <span key={i} className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded-full">{s}</span>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          {job.description && (
            <div>
              <p className="text-xs font-medium text-slate-400 mb-1.5">About the role</p>
              <p className="text-xs text-slate-300 leading-relaxed">
                {expanded ? job.description : job.description.slice(0, 300) + (job.description.length > 300 ? "..." : "")}
              </p>
              {job.description.length > 300 && (
                <button onClick={(e) => { e.stopPropagation(); setExpanded(!expanded); }}
                  className="flex items-center gap-1 text-xs text-indigo-400 mt-1 hover:text-indigo-300">
                  {expanded ? <><ChevronUp size={12} /> Show less</> : <><ChevronDown size={12} /> Read more</>}
                </button>
              )}
            </div>
          )}

          {/* Requirements */}
          {job.requirements?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-slate-400 mb-1.5">Requirements</p>
              <ul className="space-y-1">
                {job.requirements.slice(0, 4).map((r, i) => (
                  <li key={i} className="text-xs text-slate-300 flex gap-2">
                    <span className="text-slate-500 flex-shrink-0">•</span> {r}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Action buttons */}
        <div className="p-3 border-t border-slate-700 flex gap-2 flex-shrink-0">
          <button onClick={() => onSwipeLeft?.(job.id)}
            className="w-11 h-11 rounded-full border border-red-500/40 bg-red-500/10 flex items-center justify-center text-red-400 hover:bg-red-500/20 transition-all flex-shrink-0">
            <X size={18} />
          </button>

          <button onClick={handleApplyClick} disabled={actionState === "applying"}
            className="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium rounded-xl transition-all text-sm">
            {actionState === "applying" ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Tailoring resume...
              </span>
            ) : "⚡ Apply + Tailor Resume"}
          </button>

          {job.source_url && (
            <a href={job.source_url} target="_blank" rel="noopener noreferrer"
              className="w-11 h-11 rounded-full border border-slate-600 bg-slate-700/50 flex items-center justify-center text-slate-400 hover:bg-slate-600 transition-all flex-shrink-0"
              onClick={e => e.stopPropagation()}>
              <ExternalLink size={15} />
            </a>
          )}

          <button onClick={handleApplyClick} disabled={actionState === "applying"}
            className="w-11 h-11 rounded-full border border-green-500/40 bg-green-500/10 flex items-center justify-center text-green-400 hover:bg-green-500/20 transition-all flex-shrink-0 disabled:opacity-50">
            <Check size={18} />
          </button>
        </div>
      </div>
    </motion.div>
  );
}