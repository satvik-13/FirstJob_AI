import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Filter, RefreshCw, Inbox } from "lucide-react";
import JobCard from "../components/jobs/JobCard";
import ResumeDiffModal from "../components/jobs/ResumeDiffModal";
import FilterPanel from "../components/jobs/FilterPanel";
import useJobsStore from "../store/jobsStore";
import toast from "react-hot-toast";

export default function JobsPage() {
  const { jobs, currentIndex, fetchJobs, swipeLeft, applyToJob, loading } = useJobsStore();
  const [showFilters, setShowFilters] = useState(false);
  const [diffModal, setDiffModal] = useState(null);

  useEffect(() => {
    fetchJobs(true);
  }, []);

  const currentJob = jobs[currentIndex] || null;
  const nextJob = jobs[currentIndex + 1] || null;
  const remaining = jobs.length - currentIndex;

  const handleApply = async (jobId) => {
    try {
      const res = await applyToJob(jobId);
      setDiffModal({
        diff: res.data.diff,
        tailored: res.data.tailored_resume,
        summary: res.data.summary,
      });
      toast.success("Applied! Resume tailored for this role.");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to apply");
      throw err;
    }
  };

  const handleSwipeLeft = (jobId) => {
    swipeLeft(jobId);
  };

  return (
    <div className="flex flex-col bg-slate-950" style={{ height: "calc(100vh - 64px)" }}>
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 pt-4 pb-2 flex-shrink-0">
        <div>
          <h1 className="text-white font-semibold text-lg">Discover Jobs</h1>
          <p className="text-slate-400 text-xs">{remaining > 0 ? `${remaining} jobs for you` : "Loading..."}</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowFilters(!showFilters)}
            className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 hover:text-white">
            <Filter size={16} />
          </button>
          <button onClick={() => fetchJobs(true)}
            className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 hover:text-white">
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          </button>
        </div>
      </div>

      {/* Filter panel */}
      <AnimatePresence>
        {showFilters && <FilterPanel onClose={() => setShowFilters(false)} />}
      </AnimatePresence>

      {/* Card stack — takes remaining space */}
      <div className="flex-1 relative px-4 pb-4 min-h-0">
        {loading && !currentJob ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="w-10 h-10 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
              <p className="text-slate-400 text-sm">Finding jobs for you...</p>
            </div>
          </div>
        ) : !currentJob ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <Inbox size={48} className="text-slate-600 mx-auto mb-3" />
              <p className="text-slate-300 font-medium">You've seen all jobs!</p>
              <p className="text-slate-500 text-sm mt-1 mb-4">Check back tomorrow for new listings</p>
              <button onClick={() => fetchJobs(true)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm">
                Refresh
              </button>
            </div>
          </div>
        ) : (
          <div className="relative h-full max-w-sm mx-auto">
            {nextJob && (
              <div className="absolute inset-0 rounded-2xl bg-slate-800/40 border border-slate-700/50"
                style={{ transform: "scale(0.95)", zIndex: 0 }} />
            )}
            <AnimatePresence>
              {currentJob && (
                <JobCard
                  key={currentJob.id}
                  job={currentJob}
                  isTop={true}
                  onSwipeLeft={handleSwipeLeft}
                  onApply={handleApply}
                />
              )}
            </AnimatePresence>
          </div>
        )}
      </div>

      {/* Resume diff modal */}
      <AnimatePresence>
        {diffModal && (
          <ResumeDiffModal
            diff={diffModal.diff}
            summary={diffModal.summary}
            onClose={() => setDiffModal(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}