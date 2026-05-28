import { useState, useEffect } from 'react';
import { Project, AnalysisResult, Microservice, Dependency } from './types';
import { FileUpload } from './components/FileUpload';
import { GraphCanvas } from './components/GraphCanvas';
import { MetricsGrid } from './components/MetricsGrid';
import { TraceabilityTable } from './components/TraceabilityTable';
import { LayoutGrid, Layers, RefreshCw, FolderPlus, FolderOpen, Heart, Eye, ArrowRight, Trash2 } from 'lucide-react';

function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProject, setCurrentProject] = useState<Project | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  
  const [newProjectName, setNewProjectName] = useState("");
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch initial list of projects
  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/projects");
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
        if (data.length > 0 && !currentProject) {
          // Select onboarding blueprint by default
          selectProject(data[0]);
        }
      }
    } catch (err) {
      console.error("Backend offline. Fallback to offline mode.", err);
    }
  };

  const selectProject = async (project: Project) => {
    setCurrentProject(project);
    setIsLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/analysis/${project.id}`);
      if (res.ok) {
        const data = await res.json();
        setAnalysisResult(data);
      } else {
        setAnalysisResult(null);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;

    try {
      const res = await fetch("http://localhost:8000/api/v1/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newProjectName, description: "Software architecture requirements mapping project." })
      });
      if (res.ok) {
        const newProj = await res.json();
        setProjects(prev => [...prev, newProj]);
        setNewProjectName("");
        setIsCreatingProject(false);
        selectProject(newProj);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    if (!window.confirm("⚠️ Are you sure you want to delete this blueprint workspace? This will permanently wipe all generated topologies and cached services.")) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/projects/${projectId}`, {
        method: "DELETE"
      });
      if (res.ok) {
        const updated = projects.filter(p => p.id !== projectId);
        setProjects(updated);
        alert("🗑️ Blueprint deleted successfully.");
        if (updated.length > 0) {
          selectProject(updated[0]);
        } else {
          setCurrentProject(null);
          setAnalysisResult(null);
        }
      }
    } catch (err) {
      console.error(err);
      alert("Failed to delete project.");
    }
  };

  const handleSaveArchitecture = async (updatedServices: Microservice[], updatedDeps: Dependency[]) => {
    if (!analysisResult || !currentProject) return;
    
    const updatedResult: AnalysisResult = {
      ...analysisResult,
      microservices: updatedServices,
      dependencies: updatedDeps
    };

    try {
      const res = await fetch(`http://localhost:8000/api/v1/analysis/${currentProject.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedResult)
      });
      if (res.ok) {
        const data = await res.json();
        setAnalysisResult(data);
        alert("💾 System architecture updates saved successfully to backend database cache!");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to save changes. Make sure backend is running.");
    }
  };

  return (
    <div className="min-h-screen pb-16 px-4 md:px-8 max-w-[1400px] mx-auto pt-6">
      {/* Header Panel */}
      <header className="flex flex-col md:flex-row items-start md:items-center justify-between pb-6 mb-8 border-b border-slate-900">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="text-2xl">🏛️</span>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight bg-gradient-to-r from-teal-400 via-emerald-400 to-indigo-400 bg-clip-text text-transparent">
              ArchAItect
            </h1>
            <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider">
              V1.0.0 Stable
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-medium italic">
            “Transforming Software Requirements into Intelligent, Scalable Microservice Architectures.”
          </p>
        </div>
        
        {/* Project Selector bar */}
        <div className="flex items-center gap-3.5 mt-4 md:mt-0">
          <div className="flex items-center gap-2 bg-slate-900/60 border border-slate-800 px-3.5 py-2 rounded-xl text-xs">
            <FolderOpen size={14} className="text-emerald-400" />
            <select 
              value={currentProject?.id || ""} 
              onChange={(e) => {
                const proj = projects.find(p => p.id === e.target.value);
                if (proj) selectProject(proj);
              }}
              className="bg-transparent border-none focus:outline-none text-white font-semibold cursor-pointer"
            >
              <option value="" disabled className="bg-[#080b11]">Select Active Project</option>
              {projects.map(p => (
                <option key={p.id} value={p.id} className="bg-[#080b11] text-gray-200">
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={() => setIsCreatingProject(true)}
            className="flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 active:scale-95 transition-all text-xs font-semibold text-white rounded-xl border border-slate-700/50"
          >
            <FolderPlus size={14} />
            <span>New Blueprint</span>
          </button>

          {currentProject && (
            <button
              onClick={() => handleDeleteProject(currentProject.id)}
              title="Delete current blueprint"
              className="flex items-center gap-1.5 px-4 py-2 bg-rose-500/10 hover:bg-rose-500/20 active:scale-95 transition-all text-xs font-semibold text-rose-400 rounded-xl border border-rose-500/20"
            >
              <Trash2 size={14} />
              <span>Delete Blueprint</span>
            </button>
          )}
        </div>
      </header>

      {/* New Project Dialog */}
      {isCreatingProject && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center z-50 p-4">
          <form onSubmit={handleCreateProject} className="w-full max-w-md glass-panel rounded-3xl p-6 border border-slate-800 shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-2">Create Architecture Project</h3>
            <p className="text-xs text-gray-400 mb-4 leading-relaxed">
              Design a separate context workspace mapping microservices, data assets, and API routes for your platform.
            </p>
            <input 
              type="text" 
              placeholder="e.g. Ride Sharing Enterprise System"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              className="w-full bg-slate-900/80 border border-slate-800 text-sm rounded-2xl px-4 py-3 text-white focus:outline-none focus:border-emerald-500 mb-4"
              required
            />
            <div className="flex gap-2 justify-end">
              <button 
                type="button" 
                onClick={() => setIsCreatingProject(false)} 
                className="px-4 py-2 bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs font-semibold rounded-xl"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white rounded-xl border border-emerald-500/20"
              >
                Create Workspace
              </button>
            </div>
          </form>
        </div>
      )}

      {currentProject ? (
        <div className="space-y-6">
          {/* Workspace Title Grid */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-900 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div className="flex items-center gap-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-widest text-slate-500">Active Design System</span>
                <h2 className="text-xl font-extrabold text-white mt-0.5">{currentProject.name}</h2>
              </div>
              <button
                onClick={() => handleDeleteProject(currentProject.id)}
                title="Delete this blueprint workspace"
                className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 active:scale-95 transition-all text-[10px] font-bold uppercase tracking-wider text-rose-400 rounded-xl border border-rose-500/20 ml-2"
              >
                <Trash2 size={12} />
                <span>Delete</span>
              </button>
            </div>
            {analysisResult && (
              <div className="flex items-center gap-2">
                <span className="text-xs bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-xl font-mono text-gray-300">
                  📁 {analysisResult.raw_filename}
                </span>
                <button 
                  onClick={() => selectProject(currentProject)}
                  className="p-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white rounded-xl transition-all"
                  title="Reload Architecture Heuristics"
                >
                  <RefreshCw size={14} />
                </button>
              </div>
            )}
          </div>

          {/* Core Analytics Upload Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 glass-panel p-5 rounded-2xl border border-slate-900 flex flex-col justify-between h-fit">
              <div>
                <h4 className="text-sm font-extrabold uppercase tracking-widest text-white mb-2">Requirements Ingestion</h4>
                <p className="text-xs text-slate-400 mb-4 leading-relaxed font-light">
                  Input system specifications to parse. The parser segments sections and identifies boundary contexts.
                </p>
                <FileUpload onUploadSuccess={(data) => setAnalysisResult(data)} projectId={currentProject.id} />
              </div>
            </div>

            {/* Requirement Preview / Operational Context */}
            <div className="lg:col-span-2 glass-panel p-5 rounded-2xl border border-slate-900 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-3.5 border-b border-slate-800/60 mb-4">
                  <h4 className="text-sm font-extrabold uppercase tracking-widest text-white">Parsed Document Stream Preview</h4>
                  <span className="text-[10px] bg-slate-800 text-indigo-400 border border-slate-700 px-2 py-0.5 rounded font-mono font-bold">
                    PREVIEW
                  </span>
                </div>
                {analysisResult ? (
                  <div>
                    <blockquote className="text-xs text-gray-300 italic bg-slate-950/40 p-4 rounded-xl border border-slate-900 leading-relaxed font-mono max-h-[120px] overflow-y-auto">
                      "{analysisResult.raw_content_preview}"
                    </blockquote>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded font-medium">
                        ✓ {analysisResult.microservices.length} services extracted
                      </span>
                      <span className="text-[10px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded font-medium">
                        ✓ {analysisResult.dependencies.length} boundaries mapped
                      </span>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-10">
                    <p className="text-xs text-slate-500 italic">No document analyzed yet. Drag a requirements sheet to parse topology.</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Metrics Dashboard Monitoring Grid */}
          {analysisResult && (
            <div className="space-y-6">
              <MetricsGrid metrics={analysisResult.metrics} />
              
              {/* Draggable Topology Graph and Custom Inspector */}
              <div className="glass-panel p-5 rounded-3xl border border-slate-900">
                <div className="flex items-center justify-between pb-4 border-b border-slate-900 mb-6">
                  <div>
                    <h4 className="text-sm font-extrabold uppercase tracking-widest text-white">Microservice Connection Topology Mapping</h4>
                    <p className="text-xs text-slate-500 mt-1 font-light">Interactive architectural blueprint diagram. Customize routes or edit service boundaries below.</p>
                  </div>
                  <span className="text-[10px] bg-slate-800 text-indigo-400 border border-slate-700 px-2.5 py-1 rounded font-bold font-mono">
                    INTERACTIVE CANVAS
                  </span>
                </div>
                
                <GraphCanvas 
                  services={analysisResult.microservices} 
                  dependencies={analysisResult.dependencies}
                  onSaveArchitecture={handleSaveArchitecture}
                />
              </div>

              {/* Requirements Traceability Matrix */}
              <div className="glass-panel p-5 rounded-3xl border border-slate-900">
                <div className="flex items-center justify-between pb-4 border-b border-slate-900 mb-4">
                  <div>
                    <h4 className="text-sm font-extrabold uppercase tracking-widest text-white">Requirements Traceability Matrix</h4>
                    <p className="text-xs text-slate-500 mt-1 font-light">Maps each requirement sentence to the microservice boundary it justifies.</p>
                  </div>
                  <span className="text-[10px] bg-slate-800 text-indigo-400 border border-slate-700 px-2.5 py-1 rounded font-bold font-mono">
                    {analysisResult.analysis_metadata?.traceability?.length ?? 0} SERVICES TRACED
                  </span>
                </div>
                <TraceabilityTable rows={analysisResult.analysis_metadata?.traceability ?? []} />
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-20 bg-slate-900/20 rounded-3xl border border-slate-900/60 max-w-2xl mx-auto mt-12 px-6">
          <FolderPlus size={48} className="mx-auto text-emerald-500/50 mb-4" />
          <h3 className="text-lg font-bold text-white">Create your first Blueprint Workspace</h3>
          <p className="text-xs text-slate-400 mt-2 max-w-md mx-auto leading-relaxed">
            ArchAItect enables software engineering teams to analyze large legacy design requirements into microservices instantly. Establish your target project to begin.
          </p>
          <button 
            onClick={() => setIsCreatingProject(true)}
            className="mt-6 px-6 py-3 bg-gradient-to-r from-teal-500 to-emerald-500 text-xs font-bold text-white rounded-xl shadow-lg border border-emerald-400/20 hover:scale-[1.02] active:scale-95 transition-all"
          >
            Launch Design Blueprint
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
