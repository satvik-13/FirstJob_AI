import { create } from "zustand";
import api from "../services/api";

const useJobsStore = create((set, get) => ({
  jobs: [],
  currentIndex: 0,
  filters: {
    domain: "",
    location: "",
    job_type: "",
    remote_only: false,
    sort_by: "match_score",
  },
  loading: false,
  hasMore: true,
  page: 1,

  fetchJobs: async (reset = false) => {
    const { filters, page } = get();
    if (reset) set({ jobs: [], currentIndex: 0, page: 1, hasMore: true });

    set({ loading: true });
    try {
      const params = new URLSearchParams({
        page: reset ? 1 : page,
        limit: 20,
        ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
      });
      const res = await api.get(`/jobs?${params}`);
      const newJobs = res.data.jobs || [];
      set((state) => ({
        jobs: reset ? newJobs : [...state.jobs, ...newJobs],
        hasMore: newJobs.length === 20,
        page: reset ? 2 : state.page + 1,
      }));
    } catch (err) {
      console.error("Failed to fetch jobs", err);
    } finally {
      set({ loading: false });
    }
  },

  setFilters: (newFilters) => {
    set({ filters: { ...get().filters, ...newFilters } });
    get().fetchJobs(true);
  },

  // Swipe right / checkmark now triggers the full apply flow
  // (resume tailoring + recruiter outreach), not a passive save.
  applyToJob: (jobId) => {
    set((state) => ({ currentIndex: state.currentIndex + 1 }));
    return api.post(`/jobs/${jobId}/apply`);
  },

  swipeLeft: (jobId) => {
    set((state) => ({ currentIndex: state.currentIndex + 1 }));
  },

  getCurrentJob: () => {
    const { jobs, currentIndex } = get();
    return jobs[currentIndex] || null;
  },

  getUpcomingJobs: () => {
    const { jobs, currentIndex } = get();
    return jobs.slice(currentIndex, currentIndex + 3);
  },
}));

export default useJobsStore;