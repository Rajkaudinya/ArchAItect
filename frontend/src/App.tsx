import { useState, useEffect, useRef } from 'react';
import { Project, AnalysisResult, Microservice, Dependency, CompetitorIntelligence } from './types';
import { FileUpload } from './components/FileUpload';
import { GraphCanvas } from './components/GraphCanvas';
import { MetricsGrid } from './components/MetricsGrid';
import { TraceabilityTable } from './components/TraceabilityTable';
import { FlowDiagram } from './components/FlowDiagram';
import { ClarificationPanel } from './components/ClarificationPanel';
import { CompetitorIntelligencePanel } from './components/CompetitorIntelligencePanel';
import {
  RefreshCw, FolderPlus, ChevronDown, Trash2,
  Cpu, LayoutGrid, GitBranch, Table2, HelpCircle, Zap, Radar
} from 'lucide-react';

/* ── Page Loader ───────────────────────────────────────────────── */
function PageLoader() {
  return (
    <div className="page-loader">
      <div className="flex flex-col items-center gap-8">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-cyan-400 to-cyan-600 flex items-center justify-center shadow-lg">
            <span className="text-xl">🏛️</span>
          </div>
          <div>
            <h1 className="font-display text-2xl font-bold tracking-tight text-[var(--text-primary)]">
              Arch<span style={{ color: 'var(--cyan-deep)' }}>NAVI</span>tech
            </h1>
            <p className="font-mono-custom text-[9px] text-[var(--text-muted)] tracking-widest uppercase">
              Architecture Intelligence
            </p>
          </div>
        </div>

        {/* Bar loader */}
        <div className="flex flex-col items-center gap-3">
          <div className="bar-loader">
            {Array.from({ length: 12 }).map((_, i) => (
              <div key={i} className="bar-loader-bar" />
            ))}
          </div>
          <p className="font-mono-custom text-[10px] text-[var(--text-muted)] tracking-[0.2em] uppercase">
            Initialising workspace...
          </p>
        </div>

        {/* Tag row */}
        <div className="flex gap-2">
          {['NLP Engine', 'DDD Parser', 'API Generator'].map(t => (
            <span key={t} className="badge-cyan text-[9px] px-2.5 py-1 rounded-full">{t}</span>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── Blobs ─────────────────────────────────────────────────────── */
function BlobBackground() {
  return (
    <div className="blob-container">
      <div className="blob blob-1" />
      <div className="blob blob-2" />
      <div className="blob blob-3" />
      <div className="blob blob-4" />
    </div>
  );
}

/* ── Tab nav ───────────────────────────────────────────────────── */
type Tab = 'overview' | 'graph' | 'flow' | 'traceability' | 'clarify' | 'competitor';

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: 'overview',     label: 'Overview',      icon: <LayoutGrid size={13} /> },
  { id: 'flow',         label: 'Flow Diagram',   icon: <GitBranch size={13} /> },
  { id: 'clarify',      label: 'Clarifications', icon: <HelpCircle size={13} /> },
  { id: 'graph',        label: 'Topology',       icon: <Cpu size={13} /> },
  { id: 'traceability', label: 'Traceability',   icon: <Table2 size={13} /> },
  { id: 'competitor',   label: 'Competitor Intel', icon: <Radar size={13} /> },
];

/* ── App ───────────────────────────────────────────────────────── */
function App() {
  const [projects, setProjects]                 = useState<Project[]>([]);
  const [currentProject, setCurrentProject]     = useState<Project | null>(null);
  const [analysisResult, setAnalysisResult]     = useState<AnalysisResult | null>(null);
  const [newProjectName, setNewProjectName]     = useState('');
  const [isCreatingProject, setIsCreatingProject] = useState(false);
  const [isLoading, setIsLoading]               = useState(false);
  const [isClarifying, setIsClarifying]         = useState(false);
  const [isResearchingCompetitor, setIsResearchingCompetitor] = useState(false);
  const [competitorIntelligence, setCompetitorIntelligence] = useState<CompetitorIntelligence | null>(null);
  const [competitorError, setCompetitorError]   = useState('');
  const [pageReady, setPageReady]               = useState(false);
  const [activeTab, setActiveTab]               = useState<Tab>('overview');
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchProjects().finally(() => setTimeout(() => setPageReady(true), 700));
  }, []);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (dialogRef.current && !dialogRef.current.contains(e.target as Node)) {
        setIsCreatingProject(false);
      }
    };
    if (isCreatingProject) document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [isCreatingProject]);

  const fetchProjects = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/projects');
      if (res.ok) {
        const data = await res.json();
        setProjects(data);
        if (data.length > 0) selectProject(data[0]);
      }
    } catch (err) {
      console.error('Backend offline.', err);
    }
  };

  const selectProject = async (project: Project) => {
    setCurrentProject(project);
    setIsLoading(true);
    setActiveTab('overview');
    setCompetitorIntelligence(null);
    setCompetitorError('');
    try {
      const res = await fetch(`http://localhost:8000/api/v1/analysis/${project.id}`);
      if (res.ok) setAnalysisResult(await res.json());
      else setAnalysisResult(null);
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
      const res = await fetch('http://localhost:8000/api/v1/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newProjectName, description: 'Software architecture requirements mapping project.' }),
      });
      if (res.ok) {
        const newProj = await res.json();
        setProjects(prev => [...prev, newProj]);
        setNewProjectName('');
        setIsCreatingProject(false);
        selectProject(newProj);
      }
    } catch (err) { console.error(err); }
  };

  const handleDeleteProject = async (projectId: string) => {
    if (!window.confirm('⚠️ Delete this blueprint workspace? All generated topologies will be permanently wiped.')) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/projects/${projectId}`, { method: 'DELETE' });
      if (res.ok) {
        const updated = projects.filter(p => p.id !== projectId);
        setProjects(updated);
        if (updated.length > 0) selectProject(updated[0]);
        else { setCurrentProject(null); setAnalysisResult(null); }
      }
    } catch (err) { console.error(err); }
  };

  const handleClarificationSubmit = async (answers: { question: string; answer: string }[]) => {
    if (!currentProject) return;
    setIsClarifying(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/analysis/${currentProject.id}/clarify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers }),
      });
      if (res.ok) setAnalysisResult(await res.json());
      else alert('Clarification re-analysis failed.');
    } catch (err) {
      console.error(err);
      alert('Network error during clarification.');
    } finally { setIsClarifying(false); }
  };

  const handleSaveArchitecture = async (updatedServices: Microservice[], updatedDeps: Dependency[]) => {
    if (!analysisResult || !currentProject) return;
    const updatedResult: AnalysisResult = { ...analysisResult, microservices: updatedServices, dependencies: updatedDeps };
    try {
      const res = await fetch(`http://localhost:8000/api/v1/analysis/${currentProject.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedResult),
      });
      if (res.ok) { setAnalysisResult(await res.json()); alert('💾 Architecture saved!'); }
    } catch (err) { console.error(err); alert('Failed to save. Make sure backend is running.'); }
  };

  const handleCompetitorResearch = async (appType?: string) => {
    if (!currentProject) return;
    setIsResearchingCompetitor(true);
    setCompetitorError('');
    try {
      const res = await fetch(`http://localhost:8000/api/v1/analysis/${currentProject.id}/competitor-intelligence`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ app_type: appType ?? null }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.error ?? body?.detail ?? 'Competitor research failed.');
      }
      setCompetitorIntelligence(await res.json());
    } catch (err) {
      console.error(err);
      setCompetitorError(err instanceof Error ? err.message : 'Network error during competitor research.');
    } finally {
      setIsResearchingCompetitor(false);
    }
  };

  const clarificationCount = (analysisResult?.analysis_metadata?.clarifications ?? []).length;

  if (!pageReady) return <PageLoader />;

  return (
    <div className="relative min-h-screen wave-grid">
      <BlobBackground />

      <div className="relative z-10 min-h-screen pb-24">

        {/* ── Header ─────────────────────────────────────────── */}
        <header className="sticky top-0 z-40 header-stripe">
          <div className="max-w-[1440px] mx-auto px-6 md:px-10 h-16 flex items-center justify-between gap-4">
            {/* Logo */}
            <div className="flex items-center gap-3 flex-shrink-0">
              <div className="relative">
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[var(--cyan)] to-[var(--cyan-deep)] flex items-center justify-center shadow-md">
                  <span className="text-lg">🏛️</span>
                </div>
                <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-[var(--coral)] border-2 border-white pulse-cyan" />
              </div>
              <div>
                <h1 className="font-display text-xl font-bold tracking-tight text-[var(--text-primary)]">
                  Arch<span style={{ color: 'var(--cyan-deep)' }}>NAVI</span>tech
                </h1>
                <p className="font-mono-custom text-[8px] text-[var(--text-muted)] tracking-[0.15em] uppercase hidden sm:block">
                  Microservice Intelligence
                </p>
              </div>
              <span className="badge-emerald text-[8px] px-2 py-0.5 rounded-full font-bold tracking-wider uppercase hidden md:inline-flex">
                v1.0 Stable
              </span>
            </div>

            {/* Right controls */}
            <div className="flex items-center gap-2">
              {/* Project selector */}
              <div className="relative hidden sm:flex items-center gap-2 glass-panel px-3 py-1.5 rounded-xl h-9 border-[var(--border-light)]">
                <span className="section-label">Project</span>
                <div className="w-px h-3 bg-[var(--border-mid)]" />
                <select
                  value={currentProject?.id || ''}
                  onChange={e => { const p = projects.find(p => p.id === e.target.value); if (p) selectProject(p); }}
                  className="bg-transparent border-none focus:outline-none text-sm font-semibold text-[var(--text-primary)] cursor-pointer pr-5 max-w-[180px]"
                >
                  <option value="" disabled>Select project</option>
                  {projects.map(p => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
                <ChevronDown size={11} className="absolute right-2.5 text-[var(--text-muted)] pointer-events-none" />
              </div>

              <button
                onClick={() => setIsCreatingProject(true)}
                className="btn-cyan flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs"
              >
                <FolderPlus size={13} />
                <span className="hidden sm:inline">New Blueprint</span>
              </button>

              {currentProject && (
                <>
                  <button
                    onClick={() => selectProject(currentProject)}
                    className="btn-ghost p-2 rounded-xl"
                    title="Reload"
                  >
                    <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} style={{ color: 'var(--cyan-deep)' }} />
                  </button>
                  <button
                    onClick={() => handleDeleteProject(currentProject.id)}
                    className="btn-danger flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold"
                  >
                    <Trash2 size={13} />
                    <span className="hidden md:inline">Delete</span>
                  </button>
                </>
              )}
            </div>
          </div>
        </header>

        {/* ── New Project Dialog ──────────────────────────── */}
        {isCreatingProject && (
          <div className="fixed inset-0 bg-[var(--ink)]/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div ref={dialogRef} className="glass-panel bracket-accent rounded-2xl p-8 w-full max-w-md shadow-2xl stagger-in border-[var(--border-light)]">
              <div className="mb-6">
                <div className="w-10 h-10 rounded-xl bg-[var(--cyan-soft)] border border-[var(--border-cyan)] flex items-center justify-center mb-4">
                  <FolderPlus size={18} style={{ color: 'var(--cyan-deep)' }} />
                </div>
                <p className="section-label mb-1">New Workspace</p>
                <h3 className="font-display text-xl font-bold text-[var(--text-primary)]">Create Blueprint</h3>
                <p className="text-xs text-[var(--text-secondary)] mt-2 leading-relaxed">
                  Each workspace maintains isolated microservice topologies, data assets, and API routes for your platform.
                </p>
              </div>
              <form onSubmit={handleCreateProject}>
                <input
                  type="text"
                  placeholder="e.g. Ride Sharing Enterprise System"
                  value={newProjectName}
                  onChange={e => setNewProjectName(e.target.value)}
                  className="field-input w-full text-sm px-4 py-3 mb-4"
                  autoFocus
                  required
                />
                <div className="flex gap-2 justify-end">
                  <button type="button" onClick={() => setIsCreatingProject(false)} className="btn-ghost px-4 py-2 rounded-xl text-xs font-semibold">
                    Cancel
                  </button>
                  <button type="submit" className="btn-cyan px-5 py-2 rounded-xl text-xs">
                    Create Workspace
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* ── Main ───────────────────────────────────────────── */}
        <main className="max-w-[1440px] mx-auto px-6 md:px-10 pt-8">
          {currentProject ? (
            <div className="space-y-6">

              {/* Workspace header */}
              <div className="stagger-in stagger-1 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                  <p className="section-label mb-1">Active Design System</p>
                  <h2 className="font-display text-2xl md:text-3xl font-bold text-[var(--text-primary)] tracking-tight">
                    {currentProject.name}
                  </h2>
                </div>
                {analysisResult && (
                  <div className="flex items-center gap-2 flex-shrink-0 flex-wrap">
                    <span className="badge-ink text-[10px] px-3 py-1 rounded-xl flex items-center gap-1.5">
                      📁 <span className="font-mono-custom">{analysisResult.raw_filename}</span>
                    </span>
                    <span className="badge-cyan text-[10px] px-2.5 py-1 rounded-xl">
                      <strong>{analysisResult.microservices.length}</strong> services
                    </span>
                    <span className="badge-coral text-[10px] px-2.5 py-1 rounded-xl">
                      <strong>{analysisResult.dependencies.length}</strong> deps
                    </span>
                    <span className="badge-gold text-[10px] px-2.5 py-1 rounded-xl">
                      <strong>
                        {analysisResult.dependencies.length > 0
                          ? Math.round((analysisResult.dependencies.filter(d => d.type === 'async').length / analysisResult.dependencies.length) * 100)
                          : 0}%
                      </strong> async
                    </span>
                  </div>
                )}
              </div>

              {/* Upload + preview strip */}
              <div className="stagger-in stagger-2 grid grid-cols-1 lg:grid-cols-5 gap-5">
                {/* Upload */}
                <div className="lg:col-span-2 glass-panel bracket-accent p-5 rounded-2xl border-[var(--border-light)]">
                  <p className="section-label mb-1">Requirements Ingestion</p>
                  <h4 className="font-display text-sm font-bold text-[var(--text-primary)] mb-2">Upload Specification</h4>
                  <p className="text-xs text-[var(--text-secondary)] mb-4 leading-relaxed">
                    Upload SRS, BRD, or functional specs. The parser identifies bounded contexts and generates your microservice topology.
                  </p>
                  <FileUpload
                    onUploadSuccess={(data) => { setAnalysisResult(data); setActiveTab('overview'); }}
                    projectId={currentProject.id}
                  />
                </div>

                {/* Preview */}
                <div className="lg:col-span-3 glass-panel p-5 rounded-2xl border-[var(--border-light)]">
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-[var(--border-light)]">
                    <div>
                      <p className="section-label mb-1">Document Preview</p>
                      <h4 className="font-display text-sm font-bold text-[var(--text-primary)]">Parsed Content</h4>
                    </div>
                    <span className="badge-ink text-[9px] px-2.5 py-1 rounded-lg font-mono-custom">
                      {analysisResult ? analysisResult.raw_filename : 'NO FILE'}
                    </span>
                  </div>
                  {analysisResult ? (
                    <div>
                      <div
                        className="font-mono-custom text-[11px] text-[var(--text-secondary)] p-4 rounded-xl border border-[var(--border-light)] max-h-[160px] overflow-y-auto leading-relaxed whitespace-pre-wrap"
                        style={{ background: 'rgba(240,244,248,0.7)' }}
                      >
                        {analysisResult.raw_content_preview}
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <span className="badge-emerald text-[9px] px-2.5 py-1 rounded-lg">✦ {analysisResult.microservices.length} services extracted</span>
                        <span className="badge-cyan text-[9px] px-2.5 py-1 rounded-lg">⇄ {analysisResult.dependencies.length} dependencies</span>
                        <span className="badge-coral text-[9px] px-2.5 py-1 rounded-lg">
                          ⚡ {analysisResult.dependencies.length > 0
                            ? Math.round((analysisResult.dependencies.filter(d => d.type === 'async').length / analysisResult.dependencies.length) * 100)
                            : 0}% async
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-10 gap-3 text-center">
                      <div className="bar-loader opacity-40">
                        {Array.from({ length: 8 }).map((_, i) => (
                          <div key={i} className="bar-loader-bar" style={{ animationDelay: `${i * 0.1}s` }} />
                        ))}
                      </div>
                      <p className="text-xs text-[var(--text-muted)] italic">Upload a requirements file to begin parsing.</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Analysis tabs */}
              {analysisResult && (
                <div className="stagger-in stagger-3">
                  {/* Tab bar */}
                  <div className="flex items-center gap-1.5 mb-5 overflow-x-auto pb-1">
                    {TABS.map(tab => {
                      const isActive    = activeTab === tab.id;
                      const isClarify   = tab.id === 'clarify';
                      if (isClarify && clarificationCount === 0) return null;
                      return (
                        <button
                          key={tab.id}
                          onClick={() => setActiveTab(tab.id)}
                          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all duration-200 flex-shrink-0 ${
                            isActive ? 'tab-active' : 'tab-inactive'
                          }`}
                        >
                          {tab.icon}
                          {tab.label}
                          {isClarify && clarificationCount > 0 && (
                            <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded-full ${isActive ? 'bg-white/20' : 'badge-coral'}`}>
                              {clarificationCount}
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </div>

                  {/* Overview */}
                  {activeTab === 'overview' && (
                    <MetricsGrid metrics={analysisResult.metrics} />
                  )}

                  {/* Topology */}
                  {activeTab === 'graph' && (
                    <div className="glass-panel bracket-accent p-5 rounded-2xl border-[var(--border-light)]">
                      <div className="flex items-center justify-between pb-4 border-b border-[var(--border-light)] mb-5">
                        <div>
                          <p className="section-label mb-1">Interactive Canvas</p>
                          <h4 className="font-display text-base font-bold text-[var(--text-primary)]">Microservice Topology</h4>
                          <p className="text-xs text-[var(--text-secondary)] mt-1">Drag nodes to reorganise. Click to inspect bounded contexts and API endpoints.</p>
                        </div>
                        <span className="badge-cyan text-[9px] px-2.5 py-1 rounded-lg font-mono-custom">LIVE</span>
                      </div>
                      <GraphCanvas
                        services={analysisResult.microservices}
                        dependencies={analysisResult.dependencies}
                        onSaveArchitecture={handleSaveArchitecture}
                      />
                    </div>
                  )}

                  {/* Flow */}
                  {activeTab === 'flow' && (
                    <FlowDiagram mermaid={analysisResult.analysis_metadata?.flow_diagram as string ?? ''} />
                  )}

                  {/* Traceability */}
                  {activeTab === 'traceability' && (
                    <div className="glass-panel p-5 rounded-2xl border-[var(--border-light)]">
                      <div className="flex items-center justify-between pb-4 border-b border-[var(--border-light)] mb-5">
                        <div>
                          <p className="section-label mb-1">Requirements Matrix</p>
                          <h4 className="font-display text-base font-bold text-[var(--text-primary)]">Traceability Table</h4>
                          <p className="text-xs text-[var(--text-secondary)] mt-1">Maps requirement sentences to the microservice boundaries they justify.</p>
                        </div>
                        <span className="badge-gold text-[9px] px-2.5 py-1 rounded-lg font-mono-custom">
                          {analysisResult.analysis_metadata?.traceability?.length ?? 0} TRACED
                        </span>
                      </div>
                      <TraceabilityTable
                        rows={analysisResult.analysis_metadata?.traceability ?? []}
                        impactMap={(analysisResult.analysis_metadata?.impact_map ?? {}) as Record<string, string[]>}
                      />
                    </div>
                  )}

                  {/* Clarifications */}
                  {activeTab === 'clarify' && clarificationCount > 0 && (
                    <ClarificationPanel
                      questions={(analysisResult.analysis_metadata?.clarifications ?? []) as any}
                      onSubmitAnswers={handleClarificationSubmit}
                      isProcessing={isClarifying}
                    />
                  )}

                  {/* Competitor intelligence */}
                  {activeTab === 'competitor' && (
                    <CompetitorIntelligencePanel
                      intelligence={competitorIntelligence}
                      isResearching={isResearchingCompetitor}
                      error={competitorError}
                      onResearch={handleCompetitorResearch}
                    />
                  )}
                </div>
              )}
            </div>
          ) : (
            /* Empty state */
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center stagger-in">
              <div className="glass-panel bracket-accent rounded-3xl p-12 max-w-lg w-full border-[var(--border-light)]">
                <div className="w-16 h-16 rounded-2xl bg-[var(--cyan-soft)] border border-[var(--border-cyan)] flex items-center justify-center mx-auto mb-6">
                  <Zap size={28} style={{ color: 'var(--cyan-deep)' }} />
                </div>
                <h3 className="font-display text-2xl font-bold text-[var(--text-primary)] mb-2">Create your first Blueprint</h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed mb-8">
                  ArchAItect transforms large legacy design requirements into intelligent microservice architectures instantly. Start by creating a project workspace.
                </p>
                <div className="bar-loader justify-center mb-8 opacity-50">
                  {Array.from({ length: 12 }).map((_, i) => (
                    <div key={i} className="bar-loader-bar" />
                  ))}
                </div>
                <button
                  onClick={() => setIsCreatingProject(true)}
                  className="btn-cyan w-full py-3 rounded-xl text-sm"
                >
                  Launch Design Blueprint
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
