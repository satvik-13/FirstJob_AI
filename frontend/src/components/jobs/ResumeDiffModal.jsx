import { motion } from "framer-motion";
import { X, ArrowRight, Sparkles } from "lucide-react";

const TYPE_LABELS = {
  reorder: { label: "Reordered", color: "bg-blue-500/20 text-blue-300" },
  rephrase: { label: "Rephrased", color: "bg-purple-500/20 text-purple-300" },
  surface: { label: "Surfaced", color: "bg-green-500/20 text-green-300" },
  tighten: { label: "Tightened", color: "bg-yellow-500/20 text-yellow-300" },
};

export default function ResumeDiffModal({ diff = [], summary, onClose }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-end sm:items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ y: 50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        exit={{ y: 50, opacity: 0 }}
        onClick={e => e.stopPropagation()}
        className="w-full max-w-lg bg-slate-900 border border-slate-700 rounded-2xl overflow-hidden max-h-[80vh] flex flex-col"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          <div className="flex items-center gap-2">
            <Sparkles size={18} className="text-indigo-400" />
            <div>
              <p className="text-white font-medium text-sm">Resume tailored ✓</p>
              <p className="text-slate-400 text-xs">{diff?.length || 0} intelligent changes made</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-white">
            <X size={18} />
          </button>
        </div>

        {/* Summary */}
        {summary && (
          <div className="px-4 py-3 bg-indigo-500/10 border-b border-indigo-500/20">
            <p className="text-sm text-indigo-200 leading-relaxed">{summary}</p>
          </div>
        )}

        {/* Diff list */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {diff?.length === 0 && (
            <p className="text-slate-400 text-sm text-center py-4">Your resume already closely matches this job.</p>
          )}
          {diff?.map((change, i) => {
            const typeStyle = TYPE_LABELS[change.type] || TYPE_LABELS.rephrase;
            return (
              <div key={i} className="bg-slate-800/60 border border-slate-700 rounded-xl p-3">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${typeStyle.color}`}>{typeStyle.label}</span>
                  <span className="text-xs text-slate-500 capitalize">{change.section}</span>
                </div>
                <div className="space-y-2">
                  {change.original && (
                    <div className="text-xs text-red-300 bg-red-500/10 px-2 py-1.5 rounded-lg line-through opacity-70">
                      {change.original}
                    </div>
                  )}
                  {change.original && change.modified && (
                    <div className="flex justify-center"><ArrowRight size={12} className="text-slate-500" /></div>
                  )}
                  {change.modified && (
                    <div className="text-xs text-green-300 bg-green-500/10 px-2 py-1.5 rounded-lg">
                      {change.modified}
                    </div>
                  )}
                </div>
                {change.reason && (
                  <p className="text-xs text-slate-500 mt-2 italic">{change.reason}</p>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-700">
          <button onClick={onClose}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-xl transition-all">
            Great, continue applying
          </button>
          <p className="text-xs text-slate-500 text-center mt-2">Cold email to HR sent automatically in background</p>
        </div>
      </motion.div>
    </motion.div>
  );
}
