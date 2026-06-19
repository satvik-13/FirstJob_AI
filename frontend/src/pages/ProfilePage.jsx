import { useEffect, useState, useCallback } from "react";
import { User, Mail, MapPin, Code, Briefcase, GraduationCap, LogOut, Upload, FileText, CheckCircle, RefreshCw } from "lucide-react";
import { useDropzone } from "react-dropzone";
import api from "../services/api";
import useAuthStore from "../store/authStore";
import toast from "react-hot-toast";

export default function ProfilePage() {
  const { logout, user } = useAuthStore();
  const [profile, setProfile] = useState(null);
  const [gmailStatus, setGmailStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [parsing, setParsing] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [profileRes, gmailRes] = await Promise.all([
        api.get("/profile/me"),
        api.get("/auth/gmail/status"),
      ]);
      setProfile(profileRes.data);
      setGmailStatus(gmailRes.data);
    } catch {
      toast.error("Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback(async (acceptedFiles) => {
    const f = acceptedFiles[0];
    if (!f) return;
    setParsing(true);
    try {
      const formData = new FormData();
      formData.append("file", f);
      await api.post("/profile/upload-resume", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success("Resume updated successfully!");
      setShowUpload(false);
      await loadData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to parse resume");
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

  const handleConnectGmail = async () => {
    try {
      const res = await api.get("/auth/gmail/connect");
      window.location.href = res.data.auth_url;
    } catch {
      toast.error("Failed to connect Gmail");
    }
  };

  const parsed = profile?.parsed_profile;

  return (
    <div className="bg-slate-950 overflow-y-auto" style={{ height: "calc(100vh - 64px)" }}>
      <div className="max-w-2xl mx-auto p-4 pb-8 space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-white font-semibold text-xl">Profile</h1>
          <button onClick={logout} className="flex items-center gap-1.5 text-slate-400 hover:text-red-400 text-sm transition-colors">
            <LogOut size={15} /> Sign out
          </button>
        </div>

        {/* Gmail connection */}
        <div className={`border rounded-xl p-4 flex items-center justify-between
          ${gmailStatus?.connected ? "bg-green-500/10 border-green-500/30" : "bg-slate-800/50 border-slate-700"}`}>
          <div className="flex items-center gap-3">
            <Mail size={18} className={gmailStatus?.connected ? "text-green-400" : "text-slate-400"} />
            <div>
              <p className="text-white text-sm font-medium">Gmail Connection</p>
              <p className="text-xs text-slate-400">
                {gmailStatus?.connected ? "✓ Connected — cold emails sent from your account" : "Connect to enable cold outreach to HRs"}
              </p>
            </div>
          </div>
          {!gmailStatus?.connected && (
            <button onClick={handleConnectGmail}
              className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs rounded-lg">
              Connect
            </button>
          )}
        </div>

        {/* Resume upload toggle */}
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-white text-sm font-medium flex items-center gap-2">
              <FileText size={15} className="text-indigo-400" />
              {parsed ? "Resume uploaded" : "No resume uploaded"}
            </p>
            <button onClick={() => setShowUpload(!showUpload)}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 rounded-lg hover:bg-indigo-600/30 transition-all">
              <Upload size={12} /> {parsed ? "Update Resume" : "Upload Resume"}
            </button>
          </div>

          {showUpload && (
            <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all
              ${isDragActive ? "border-indigo-400 bg-indigo-500/10" : "border-slate-600 hover:border-indigo-500"}
              ${parsing ? "opacity-50 cursor-not-allowed" : ""}`}>
              <input {...getInputProps()} />
              {parsing ? (
                <div className="flex flex-col items-center gap-2">
                  <RefreshCw size={20} className="text-indigo-400 animate-spin" />
                  <p className="text-indigo-300 text-sm">Parsing with AI...</p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2">
                  <Upload size={20} className="text-slate-400" />
                  <p className="text-slate-300 text-sm">Drop your resume here or click to browse</p>
                  <p className="text-slate-500 text-xs">PDF or DOCX • Max 5MB</p>
                </div>
              )}
            </div>
          )}

          {parsed && !showUpload && (
            <p className="text-xs text-slate-500">
              {profile?.resume_filename} • {parsed.skills?.length || 0} skills extracted
            </p>
          )}
        </div>

        {loading ? (
          <div className="text-center py-8 text-slate-400">Loading profile...</div>
        ) : !parsed ? (
          <div className="text-center py-8">
            <p className="text-slate-400">Upload your resume to see your profile</p>
          </div>
        ) : (
          <>
            {/* Basic info */}
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 rounded-full bg-indigo-500/20 flex items-center justify-center">
                  <User size={22} className="text-indigo-400" />
                </div>
                <div>
                  <p className="text-white font-medium">{parsed.full_name || user?.full_name}</p>
                  <p className="text-slate-400 text-sm">{parsed.email}</p>
                </div>
              </div>
              {parsed.location && (
                <p className="text-slate-400 text-sm flex items-center gap-1.5 mb-2">
                  <MapPin size={13} /> {parsed.location}
                </p>
              )}
              {parsed.summary && (
                <p className="text-slate-300 text-sm leading-relaxed">{parsed.summary}</p>
              )}
            </div>

            {/* Skills */}
            {parsed.skills?.length > 0 && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                <p className="text-white font-medium text-sm flex items-center gap-2 mb-3">
                  <Code size={15} /> Skills ({parsed.skills.length})
                </p>
                <div className="flex flex-wrap gap-2">
                  {parsed.skills.map((s, i) => (
                    <span key={i} className="text-xs bg-indigo-500/15 text-indigo-300 border border-indigo-500/25 px-2.5 py-1 rounded-full">{s}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Experience */}
            {parsed.experience?.length > 0 && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                <p className="text-white font-medium text-sm flex items-center gap-2 mb-3">
                  <Briefcase size={15} /> Experience
                </p>
                <div className="space-y-4">
                  {parsed.experience.map((exp, i) => (
                    <div key={i} className={i > 0 ? "pt-4 border-t border-slate-700" : ""}>
                      <p className="text-white text-sm font-medium">{exp.title}</p>
                      <p className="text-slate-400 text-xs">{exp.company} · {exp.start_date} – {exp.end_date || "Present"}</p>
                      <ul className="mt-2 space-y-1">
                        {exp.bullets?.slice(0, 3).map((b, j) => (
                          <li key={j} className="text-slate-300 text-xs flex gap-2">
                            <span className="text-slate-500 mt-0.5 flex-shrink-0">•</span> {b}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Projects */}
            {parsed.projects?.length > 0 && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                <p className="text-white font-medium text-sm flex items-center gap-2 mb-3">
                  <Code size={15} /> Projects
                </p>
                <div className="space-y-3">
                  {parsed.projects.map((proj, i) => (
                    <div key={i} className={i > 0 ? "pt-3 border-t border-slate-700" : ""}>
                      <p className="text-white text-sm font-medium">{proj.name}</p>
                      {proj.tech_stack?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {proj.tech_stack.map((t, j) => (
                            <span key={j} className="text-xs bg-slate-700 text-slate-300 px-2 py-0.5 rounded">{t}</span>
                          ))}
                        </div>
                      )}
                      {proj.description && <p className="text-slate-400 text-xs mt-1">{proj.description}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Education */}
            {parsed.education?.length > 0 && (
              <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4">
                <p className="text-white font-medium text-sm flex items-center gap-2 mb-3">
                  <GraduationCap size={15} /> Education
                </p>
                {parsed.education.map((edu, i) => (
                  <div key={i}>
                    <p className="text-white text-sm">{edu.institution}</p>
                    <p className="text-slate-400 text-xs">{edu.degree} {edu.field && `in ${edu.field}`} · {edu.year}</p>
                    {edu.gpa && <p className="text-slate-500 text-xs">GPA: {edu.gpa}</p>}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
