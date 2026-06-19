import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, CheckCircle, ArrowRight, Briefcase, MapPin } from "lucide-react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import toast from "react-hot-toast";

const DOMAINS = [
  { id: "software_engineering", label: "Software Engineering", emoji: "💻" },
  { id: "data_science", label: "Data Science / ML", emoji: "📊" },
  { id: "product_management", label: "Product Management", emoji: "🎯" },
  { id: "design", label: "UI/UX Design", emoji: "🎨" },
  { id: "marketing", label: "Marketing / Growth", emoji: "📣" },
  { id: "finance", label: "Finance / Accounting", emoji: "💰" },
  { id: "consulting", label: "Consulting", emoji: "🏢" },
  { id: "other", label: "Other", emoji: "🔍" },
];

const JOB_TYPES = [
  { id: "full_time", label: "Full-time" },
  { id: "internship", label: "Internship" },
  { id: "remote", label: "Remote" },
  { id: "hybrid", label: "Hybrid" },
  { id: "contract", label: "Contract" },
];

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [file, setFile] = useState(null);
  const [parsing, setParsing] = useState(false);
  const [parsedProfile, setParsedProfile] = useState(null);
  const [preferences, setPreferences] = useState({
    domain: "",
    sub_domains: [],
    locations: [],
    job_types: ["full_time"],
    salary_min: null,
    salary_max: null,
    open_to_remote: true,
    experience_level: "fresher",
  });
  const [locationInput, setLocationInput] = useState("");
  const [saving, setSaving] = useState(false);

  const onDrop = useCallback(async (acceptedFiles) => {
    const f = acceptedFiles[0];
    if (!f) return;
    setFile(f);
    setParsing(true);
    try {
      const formData = new FormData();
      formData.append("file", f);
      const res = await api.post("/profile/upload-resume", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setParsedProfile(res.data.parsed);
      toast.success("Resume parsed successfully!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to parse resume");
      setFile(null);
    } finally {
      setParsing(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"] },
    maxFiles: 1,
    disabled: parsing,
  });

  const addLocation = () => {
    if (locationInput.trim() && !preferences.locations.includes(locationInput.trim())) {
      setPreferences(p => ({ ...p, locations: [...p.locations, locationInput.trim()] }));
      setLocationInput("");
    }
  };

  const toggleJobType = (id) => {
    setPreferences(p => ({
      ...p,
      job_types: p.job_types.includes(id)
        ? p.job_types.filter(t => t !== id)
        : [...p.job_types, id],
    }));
  };

  const toggleDomain = (id) => {
    // First domain selected becomes the primary domain
    // Additional ones go into sub_domains
    if (preferences.domain === id) {
      // Deselect primary — promote first sub_domain if exists
      const newSubs = preferences.sub_domains.filter(d => d !== id);
      setPreferences(p => ({
        ...p,
        domain: newSubs[0] || "",
        sub_domains: newSubs.slice(1),
      }));
    } else if (preferences.sub_domains.includes(id)) {
      setPreferences(p => ({
        ...p,
        sub_domains: p.sub_domains.filter(d => d !== id),
      }));
    } else if (!preferences.domain) {
      setPreferences(p => ({ ...p, domain: id }));
    } else {
      setPreferences(p => ({ ...p, sub_domains: [...p.sub_domains, id] }));
    }
  };

  const isDomainSelected = (id) =>
    preferences.domain === id || preferences.sub_domains.includes(id);

  const handleSavePreferences = async () => {
    if (!preferences.domain) { toast.error("Please select at least one domain"); return; }
    setSaving(true);
    try {
      await api.put("/profile/preferences", preferences);
      toast.success("You're all set!");
      navigate("/jobs");
    } catch (err) {
      toast.error("Failed to save preferences");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 flex items-center justify-center p-4">
      <div className="w-full max-w-xl">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">FirstJob <span className="text-indigo-400">AI</span></h1>
          <p className="text-slate-400 mt-1">Your AI-powered job search co-pilot</p>
        </div>

        <div className="flex items-center justify-center gap-3 mb-8">
          {[1, 2].map(s => (
            <div key={s} className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all
                ${step >= s ? "bg-indigo-500 text-white" : "bg-slate-700 text-slate-400"}`}>
                {step > s ? <CheckCircle size={16} /> : s}
              </div>
              {s < 2 && <div className={`w-16 h-0.5 ${step > s ? "bg-indigo-500" : "bg-slate-700"}`} />}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div key="step1" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
              <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6">
                <h2 className="text-xl font-semibold text-white mb-1">Upload your resume</h2>
                <p className="text-slate-400 text-sm mb-6">PDF or DOCX. Our AI will parse it — we never fabricate your experience.</p>

                <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
                  ${isDragActive ? "border-indigo-400 bg-indigo-500/10" : "border-slate-600 hover:border-indigo-500 hover:bg-slate-700/30"}
                  ${parsing ? "opacity-50 cursor-not-allowed" : ""}`}>
                  <input {...getInputProps()} />
                  {parsing ? (
                    <div className="flex flex-col items-center gap-3">
                      <div className="w-8 h-8 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
                      <p className="text-indigo-300 text-sm">Parsing your resume with AI...</p>
                    </div>
                  ) : file ? (
                    <div className="flex flex-col items-center gap-3">
                      <FileText size={32} className="text-indigo-400" />
                      <p className="text-white font-medium">{file.name}</p>
                      <p className="text-green-400 text-sm flex items-center gap-1"><CheckCircle size={14} /> Parsed successfully</p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center gap-3">
                      <Upload size={32} className="text-slate-400" />
                      <p className="text-slate-300">Drag & drop your resume here</p>
                      <p className="text-slate-500 text-sm">or click to browse</p>
                      <p className="text-slate-600 text-xs">PDF or DOCX • Max 5MB</p>
                    </div>
                  )}
                </div>

                {parsedProfile && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-4 p-4 bg-slate-700/40 rounded-xl">
                    <p className="text-sm text-slate-300 font-medium mb-2">Extracted from your resume:</p>
                    <div className="flex flex-wrap gap-2">
                      {parsedProfile.skills?.slice(0, 8).map(s => (
                        <span key={s} className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded-full">{s}</span>
                      ))}
                      {parsedProfile.skills?.length > 8 && (
                        <span className="text-xs text-slate-400">+{parsedProfile.skills.length - 8} more</span>
                      )}
                    </div>
                  </motion.div>
                )}

                <button onClick={() => setStep(2)} disabled={!parsedProfile}
                  className="w-full mt-4 py-3 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium rounded-xl transition-all flex items-center justify-center gap-2">
                  Next: Set your preferences <ArrowRight size={16} />
                </button>
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
              <div className="bg-slate-800/50 border border-slate-700 rounded-2xl p-6 space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-white mb-1">Your job preferences</h2>
                  <p className="text-slate-400 text-sm">Select multiple domains — we'll tailor resumes for each.</p>
                </div>

                {/* Domain - multi select */}
                <div>
                  <label className="text-sm font-medium text-slate-300 flex items-center gap-2 mb-1">
                    <Briefcase size={14} /> Career domain
                  </label>
                  <p className="text-xs text-slate-500 mb-3">Select all that apply — AI will adapt your resume per role</p>
                  <div className="grid grid-cols-2 gap-2">
                    {DOMAINS.map(d => (
                      <button key={d.id} onClick={() => toggleDomain(d.id)}
                        className={`py-2.5 px-3 rounded-xl text-sm font-medium text-left transition-all border relative
                          ${isDomainSelected(d.id)
                            ? "bg-indigo-600/30 border-indigo-500 text-indigo-200"
                            : "bg-slate-700/40 border-slate-600 text-slate-300 hover:border-slate-500"}`}>
                        {d.emoji} {d.label}
                        {preferences.domain === d.id && (
                          <span className="absolute top-1 right-1 text-xs bg-indigo-500 text-white px-1 rounded">primary</span>
                        )}
                      </button>
                    ))}
                  </div>
                  {(preferences.domain || preferences.sub_domains.length > 0) && (
                    <p className="text-xs text-indigo-300 mt-2">
                      Selected: {[preferences.domain, ...preferences.sub_domains].filter(Boolean).map(id => DOMAINS.find(d => d.id === id)?.label).join(", ")}
                    </p>
                  )}
                </div>

                {/* Job types - multi select */}
                <div>
                  <label className="text-sm font-medium text-slate-300 mb-3 block">Job type (select all that apply)</label>
                  <div className="flex flex-wrap gap-2">
                    {JOB_TYPES.map(t => (
                      <button key={t.id} onClick={() => toggleJobType(t.id)}
                        className={`py-1.5 px-3 rounded-full text-sm transition-all border
                          ${preferences.job_types.includes(t.id)
                            ? "bg-indigo-600/30 border-indigo-500 text-indigo-200"
                            : "bg-slate-700/40 border-slate-600 text-slate-300"}`}>
                        {t.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Locations */}
                <div>
                  <label className="text-sm font-medium text-slate-300 flex items-center gap-2 mb-3"><MapPin size={14} /> Preferred locations</label>
                  <div className="flex gap-2">
                    <input value={locationInput} onChange={e => setLocationInput(e.target.value)}
                      onKeyDown={e => e.key === "Enter" && addLocation()}
                      placeholder="e.g. Bangalore, Remote, Mumbai..."
                      className="flex-1 bg-slate-700/50 border border-slate-600 text-white placeholder-slate-500 rounded-xl px-3 py-2 text-sm focus:outline-none focus:border-indigo-500" />
                    <button onClick={addLocation} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-sm">Add</button>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {preferences.locations.map(l => (
                      <span key={l} className="text-xs bg-slate-600/50 text-slate-300 px-2 py-1 rounded-full flex items-center gap-1">
                        {l}
                        <button onClick={() => setPreferences(p => ({ ...p, locations: p.locations.filter(x => x !== l) }))} className="text-slate-500 hover:text-red-400">×</button>
                      </span>
                    ))}
                  </div>
                </div>

                <button onClick={handleSavePreferences} disabled={saving}
                  className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium rounded-xl transition-all flex items-center justify-center gap-2">
                  {saving ? "Saving..." : <>Start discovering jobs <ArrowRight size={16} /></>}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
