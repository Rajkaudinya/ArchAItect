import React, { useState, useEffect } from 'react';
import { Microservice, Dependency, ApiEndpoint } from '../types';
import { Settings, Database, Network, Plus, Trash2, X, Save } from 'lucide-react';

interface GraphCanvasProps {
  services: Microservice[];
  dependencies: Dependency[];
  onSaveArchitecture: (updatedServices: Microservice[], updatedDeps: Dependency[]) => void;
}

const METHOD_COLORS: Record<string, { text: string; bg: string; border: string }> = {
  GET:    { text: '#059669', bg: 'var(--emerald-soft)', border: 'rgba(0,200,117,0.25)' },
  POST:   { text: 'var(--cyan-deep)', bg: 'var(--cyan-soft)', border: 'var(--border-cyan)' },
  PUT:    { text: '#b45309', bg: 'var(--gold-soft)', border: 'rgba(247,183,49,0.3)' },
  DELETE: { text: 'var(--coral-deep)', bg: 'var(--coral-soft)', border: 'rgba(255,92,92,0.25)' },
};

export const GraphCanvas: React.FC<GraphCanvasProps> = ({
  services: initialServices,
  dependencies: initialDeps,
  onSaveArchitecture,
}) => {
  const [services,        setServices]       = useState<Microservice[]>(initialServices);
  const [dependencies,    setDependencies]   = useState<Dependency[]>(initialDeps);
  const [selectedService, setSelectedService] = useState<Microservice | null>(null);
  const [positions,       setPositions]      = useState<Record<string, { x: number; y: number }>>({});
  const [draggingNode,    setDraggingNode]   = useState<string | null>(null);
  const [dragOffset,      setDragOffset]     = useState({ x: 0, y: 0 });

  useEffect(() => {
    setServices(initialServices);
    setDependencies(initialDeps);

    const newPositions: Record<string, { x: number; y: number }> = {};
    const radiusX = 300; const radiusY = 160;
    const centerX = 400; const centerY = 240;

    initialServices.forEach((service, index) => {
      const angle = (index / initialServices.length) * 2 * Math.PI;
      newPositions[service.id] = {
        x: centerX + radiusX * Math.cos(angle) - 90,
        y: centerY + radiusY * Math.sin(angle) - 45,
      };
    });
    setPositions(newPositions);
    setSelectedService(null);
  }, [initialServices, initialDeps]);

  const handleMouseDown = (serviceId: string, e: React.MouseEvent) => {
    e.preventDefault();
    setDraggingNode(serviceId);
    const pos = positions[serviceId] || { x: 100, y: 100 };
    setDragOffset({ x: e.clientX - pos.x, y: e.clientY - pos.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (draggingNode) {
      setPositions(prev => ({
        ...prev,
        [draggingNode]: { x: e.clientX - dragOffset.x, y: e.clientY - dragOffset.y },
      }));
    }
  };

  const handleMouseUp = () => setDraggingNode(null);

  const handleUpdateServiceName = (id: string, newName: string) => {
    const updated = services.map(s => s.id === id ? { ...s, name: newName } : s);
    setServices(updated);
    if (selectedService?.id === id) setSelectedService(prev => prev ? { ...prev, name: newName } : null);
  };

  const handleUpdateServiceDescription = (id: string, newDesc: string) => {
    const updated = services.map(s => s.id === id ? { ...s, description: newDesc } : s);
    setServices(updated);
    if (selectedService?.id === id) setSelectedService(prev => prev ? { ...prev, description: newDesc } : null);
  };

  const handleUpdateDatabase = (id: string, db: string, dbReasoning: string) => {
    const updated = services.map(s => s.id === id ? { ...s, database: db, database_reasoning: dbReasoning } : s);
    setServices(updated);
    if (selectedService?.id === id) setSelectedService(prev => prev ? { ...prev, database: db, database_reasoning: dbReasoning } : null);
  };

  const handleAddApi = (serviceId: string) => {
    const newApi: ApiEndpoint = { path: '/api/v1/new-endpoint', method: 'GET', description: 'Custom endpoint.' };
    const updated = services.map(s => s.id === serviceId ? { ...s, apis: [...s.apis, newApi] } : s);
    setServices(updated);
    setSelectedService(updated.find(s => s.id === serviceId) ?? null);
  };

  const handleRemoveApi = (serviceId: string, index: number) => {
    const updated = services.map(s => s.id === serviceId ? { ...s, apis: s.apis.filter((_, i) => i !== index) } : s);
    setServices(updated);
    setSelectedService(updated.find(s => s.id === serviceId) ?? null);
  };

  const handleUpdateApi = (serviceId: string, index: number, field: keyof ApiEndpoint, value: string) => {
    const updated = services.map(s => {
      if (s.id !== serviceId) return s;
      const newApis = [...s.apis];
      newApis[index] = { ...newApis[index], [field]: value };
      return { ...s, apis: newApis };
    });
    setServices(updated);
    setSelectedService(updated.find(s => s.id === serviceId) ?? null);
  };

  const handleAddServiceNode = () => {
    const rawId = `custom-service-${Date.now()}`;
    const newService: Microservice = {
      id: rawId,
      name: 'Custom Microservice',
      description: 'User-defined software domain service.',
      domain: 'Custom Bounded Context',
      database: 'PostgreSQL',
      database_reasoning: 'Selected based on schema modeling constraints.',
      apis: [{ path: '/api/v1/health', method: 'GET', description: 'Default health check.' }],
      scaling_recommendations: ['Distribute container replicas across server instances'],
    };
    setServices(prev => [...prev, newService]);
    setPositions(prev => ({ ...prev, [rawId]: { x: 350 + Math.random() * 50, y: 200 + Math.random() * 50 } }));
  };

  const handleRemoveServiceNode = (serviceId: string) => {
    setServices(prev => prev.filter(s => s.id !== serviceId));
    setDependencies(prev => prev.filter(d => d.source !== serviceId && d.target !== serviceId));
    setSelectedService(null);
  };

  return (
    <div className="flex flex-col lg:flex-row gap-4 h-[640px]">
      {/* Canvas */}
      <div
        className="flex-1 relative overflow-hidden rounded-2xl border border-[var(--border-light)] canvas-bg"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* Toolbar */}
        <div className="absolute top-3 left-3 z-10 flex gap-2">
          <button
            onClick={handleAddServiceNode}
            className="btn-cyan flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-[11px]"
          >
            <Plus size={12} />
            Add Service
          </button>
          <button
            onClick={() => onSaveArchitecture(services, dependencies)}
            className="btn-ghost flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-[11px] font-semibold"
          >
            <Save size={12} style={{ color: 'var(--emerald)' }} />
            Save
          </button>
        </div>

        <div className="absolute top-3 right-3 z-10 flex items-center gap-2">
          <div className="flex items-center gap-3 glass-panel px-3 py-1.5 rounded-xl text-[9px] font-mono-custom text-[var(--text-muted)] border-[var(--border-light)]">
            <span className="flex items-center gap-1.5">
              <span className="w-4 h-px" style={{ background: 'var(--cyan-deep)' }} />sync
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-4 h-px" style={{ background: '#7c3aed', borderTop: '1px dashed #7c3aed' }} />async
            </span>
          </div>
          <div className="glass-panel px-3 py-1.5 rounded-xl font-mono-custom text-[9px] text-[var(--text-muted)] border-[var(--border-light)]">
            Drag to reorganise · click to inspect
          </div>
        </div>

        {/* SVG arrows */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
          <defs>
            <marker id="arrow-sync" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#00a8be" />
            </marker>
            <marker id="arrow-async" viewBox="0 0 10 10" refX="18" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#7c3aed" />
            </marker>
            <filter id="glow-cyan">
              <feGaussianBlur stdDeviation="1.5" result="coloredBlur" />
              <feMerge><feMergeNode in="coloredBlur" /><feMergeNode in="SourceGraphic" /></feMerge>
            </filter>
          </defs>

          {dependencies.map((dep, idx) => {
            const start = positions[dep.source];
            const end   = positions[dep.target];
            if (!start || !end) return null;
            const sX = start.x + 90; const sY = start.y + 45;
            const eX = end.x + 90;   const eY = end.y + 45;
            const isAsync = dep.type === 'async';
            return (
              <g key={`dep-${idx}`}>
                <path
                  d={`M ${sX} ${sY} Q ${(sX + eX) / 2} ${(sY + eY) / 2 - 28}, ${eX} ${eY}`}
                  fill="none"
                  stroke={isAsync ? '#7c3aed' : '#00a8be'}
                  strokeWidth={1.5}
                  strokeDasharray={isAsync ? '5,4' : 'none'}
                  markerEnd={isAsync ? 'url(#arrow-async)' : 'url(#arrow-sync)'}
                  opacity={0.55}
                  filter="url(#glow-cyan)"
                  className="hover:opacity-100 transition-opacity"
                />
              </g>
            );
          })}
        </svg>

        {/* Draggable nodes */}
        <div className="absolute inset-0 pointer-events-none">
          {services.map((service) => {
            const pos        = positions[service.id] || { x: 100, y: 100 };
            const isSelected = selectedService?.id === service.id;
            const cohesion   = service.metadata?.cohesion_score as number | undefined;

            return (
              <div
                key={service.id}
                style={{ left: `${pos.x}px`, top: `${pos.y}px`, position: 'absolute' }}
                onMouseDown={e => handleMouseDown(service.id, e)}
                onClick={() => setSelectedService(service)}
                className={`w-[185px] pointer-events-auto node-draggable glass-panel rounded-2xl p-3 select-none border transition-all ${
                  isSelected
                    ? 'border-[var(--cyan)] shadow-[0_0_20px_rgba(0,212,232,0.25),0_4px_20px_rgba(0,0,0,0.1)]'
                    : 'border-[var(--border-light)] hover:border-[var(--cyan-mid)] hover:shadow-md'
                }`}
              >
                {/* Top accent line on selected */}
                {isSelected && (
                  <div className="absolute top-0 left-4 right-4 h-[2px] rounded-b-sm" style={{ background: 'linear-gradient(90deg, transparent, var(--cyan), transparent)' }} />
                )}

                <div className="flex items-start justify-between gap-1 mb-2">
                  <span className="font-mono-custom text-[8px] text-[var(--text-muted)] uppercase tracking-wider truncate">
                    {service.domain}
                  </span>
                  <Database size={9} style={{ color: 'var(--cyan-deep)' }} className="flex-shrink-0 mt-0.5" />
                </div>

                <h5 className="font-display text-[11px] font-bold text-[var(--text-primary)] leading-tight mb-2.5 truncate">
                  {service.name}
                </h5>

                <div className="flex items-center justify-between pt-2 border-t border-[var(--border-light)]">
                  <span className="badge-cyan font-mono-custom text-[8px] px-1.5 py-0.5 rounded-lg">
                    {service.database.split(' ')[0]}
                  </span>
                  <div className="flex items-center gap-1.5">
                    {cohesion !== undefined && (
                      <span
                        title={`Cohesion: ${Math.round(cohesion)}%`}
                        className={`font-mono-custom text-[8px] font-bold px-1.5 py-0.5 rounded-lg ${
                          cohesion >= 70 ? 'badge-emerald' : cohesion >= 40 ? 'badge-gold' : 'badge-coral'
                        }`}
                      >
                        C:{Math.round(cohesion)}%
                      </span>
                    )}
                    <span className="font-mono-custom text-[8px] text-[var(--text-muted)]">
                      {service.apis.length} APIs
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Inspector */}
      <div className="w-full lg:w-[370px] glass-panel rounded-2xl border-[var(--border-light)] overflow-y-auto flex flex-col">
        {selectedService ? (
          <div className="flex flex-col h-full">
            {/* Panel header */}
            <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border-light)] flex-shrink-0" style={{ background: 'rgba(0,212,232,0.03)' }}>
              <div>
                <p className="section-label mb-0.5">Bounded Context Inspector</p>
                <h5 className="font-display text-sm font-bold text-[var(--text-primary)] truncate max-w-[200px]">
                  {selectedService.name}
                </h5>
              </div>
              <div className="flex gap-1.5 flex-shrink-0">
                <button
                  onClick={() => handleRemoveServiceNode(selectedService.id)}
                  className="btn-danger p-2 rounded-xl"
                  title="Delete service"
                >
                  <Trash2 size={12} />
                </button>
                <button
                  onClick={() => setSelectedService(null)}
                  className="btn-ghost p-2 rounded-xl"
                >
                  <X size={12} />
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              {/* Name */}
              <div>
                <label className="section-label block mb-1.5">Service Name</label>
                <input
                  type="text"
                  value={selectedService.name}
                  onChange={e => handleUpdateServiceName(selectedService.id, e.target.value)}
                  className="field-input w-full text-xs font-semibold px-3 py-2"
                />
              </div>

              {/* Domain */}
              <div>
                <label className="section-label block mb-1.5">Bounded Context Domain</label>
                <div className="badge-cyan font-mono-custom text-xs px-3 py-2 rounded-xl">
                  {selectedService.domain}
                </div>
              </div>

              {/* Cohesion */}
              {selectedService.metadata?.cohesion_score !== undefined && (() => {
                const score  = Math.round(selectedService.metadata.cohesion_score as number);
                const color  = score >= 70 ? 'var(--emerald)' : score >= 40 ? 'var(--gold)' : 'var(--coral)';
                const label  = score >= 70 ? 'High Cohesion' : score >= 40 ? 'Moderate' : 'Low Cohesion';
                return (
                  <div>
                    <label className="section-label block mb-1.5">Domain Cohesion</label>
                    <div className="flex items-center gap-3">
                      <div className="flex-1 h-1.5 rounded-full bg-[var(--border-light)] overflow-hidden">
                        <div
                          className="h-full rounded-full metric-bar-fill"
                          style={{ width: `${score}%`, background: color }}
                        />
                      </div>
                      <span className="font-mono-custom text-[10px] font-bold text-[var(--text-primary)] w-8 text-right">{score}%</span>
                      <span className="font-mono-custom text-[9px] text-[var(--text-muted)]">{label}</span>
                    </div>
                  </div>
                );
              })()}

              {/* Description */}
              <div>
                <label className="section-label block mb-1.5">Core Responsibilities</label>
                <textarea
                  rows={2}
                  value={selectedService.description}
                  onChange={e => handleUpdateServiceDescription(selectedService.id, e.target.value)}
                  className="field-input w-full text-xs px-3 py-2 resize-none leading-relaxed"
                />
              </div>

              {/* Database */}
              <div className="pt-3 border-t border-[var(--border-light)]">
                <div className="flex items-center gap-1.5 mb-2">
                  <Database size={11} style={{ color: 'var(--cyan-deep)' }} />
                  <label className="font-display text-xs font-bold text-[var(--text-primary)]">Database</label>
                </div>
                <input
                  type="text"
                  value={selectedService.database}
                  onChange={e => handleUpdateDatabase(selectedService.id, e.target.value, selectedService.database_reasoning)}
                  className="field-input w-full text-xs font-semibold px-3 py-2 mb-2"
                  style={{ color: 'var(--cyan-deep)' }}
                />
                <p className="font-mono-custom text-[9px] text-[var(--text-secondary)] leading-relaxed p-2.5 rounded-xl border border-[var(--border-light)] italic" style={{ background: 'rgba(240,244,248,0.7)' }}>
                  {selectedService.database_reasoning}
                </p>
              </div>

              {/* Endpoints */}
              <div className="pt-3 border-t border-[var(--border-light)]">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-1.5">
                    <Network size={11} style={{ color: 'var(--cyan-deep)' }} />
                    <label className="font-display text-xs font-bold text-[var(--text-primary)]">REST Endpoints</label>
                    <span className="badge-cyan font-mono-custom text-[8px] px-1.5 py-0.5 rounded-lg">
                      {selectedService.apis.length}
                    </span>
                  </div>
                  <button
                    onClick={() => handleAddApi(selectedService.id)}
                    className="btn-ghost p-1.5 rounded-lg"
                    style={{ color: 'var(--emerald)' }}
                  >
                    <Plus size={11} />
                  </button>
                </div>

                <div className="space-y-2 max-h-[200px] overflow-y-auto pr-1">
                  {selectedService.apis.map((api, idx) => {
                    const mc = METHOD_COLORS[api.method] ?? { text: 'var(--text-secondary)', bg: 'var(--bg-deep)', border: 'var(--border-light)' };
                    return (
                      <div
                        key={idx}
                        className="p-3 rounded-xl border space-y-2"
                        style={{ background: 'rgba(240,244,248,0.6)', borderColor: 'var(--border-light)' }}
                      >
                        <div className="flex items-center gap-2">
                          <select
                            value={api.method}
                            onChange={e => handleUpdateApi(selectedService.id, idx, 'method', e.target.value)}
                            className="font-mono-custom text-[10px] font-bold px-1.5 py-0.5 rounded-lg border focus:outline-none w-16"
                            style={{ color: mc.text, background: mc.bg, borderColor: mc.border }}
                          >
                            {['GET', 'POST', 'PUT', 'DELETE'].map(m => (
                              <option key={m} value={m}>{m}</option>
                            ))}
                          </select>
                          <input
                            type="text"
                            value={api.path}
                            onChange={e => handleUpdateApi(selectedService.id, idx, 'path', e.target.value)}
                            className="flex-1 field-input font-mono-custom text-[10px] px-2 py-0.5 rounded-lg"
                          />
                          <button
                            onClick={() => handleRemoveApi(selectedService.id, idx)}
                            className="text-[var(--text-muted)] hover:text-[var(--coral)] transition-colors"
                          >
                            <Trash2 size={10} />
                          </button>
                        </div>
                        <input
                          type="text"
                          value={api.description}
                          onChange={e => handleUpdateApi(selectedService.id, idx, 'description', e.target.value)}
                          className="w-full bg-transparent font-mono-custom text-[9px] text-[var(--text-muted)] border-b border-transparent hover:border-[var(--border-mid)] focus:border-[var(--cyan)] focus:outline-none py-0.5 transition-colors"
                          placeholder="Description..."
                        />
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
            <div className="w-12 h-12 rounded-2xl bg-[var(--bg-deep)] border border-[var(--border-light)] flex items-center justify-center mb-4">
              <Settings size={20} className="text-[var(--text-muted)] animate-spin-slow" />
            </div>
            <h5 className="font-display text-sm font-bold text-[var(--text-secondary)] mb-2">Inspector Empty</h5>
            <p className="text-xs text-[var(--text-muted)] leading-relaxed max-w-[200px]">
              Click any microservice node on the canvas to inspect its parameters and endpoints.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};