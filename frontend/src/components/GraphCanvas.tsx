import React, { useState, useEffect } from 'react';
import { Microservice, Dependency, ApiEndpoint } from '../types';
import { Settings, Database, Network, Key, Plus, Trash2, Edit3, X, Save, RefreshCw } from 'lucide-react';

interface GraphCanvasProps {
  services: Microservice[];
  dependencies: Dependency[];
  onSaveArchitecture: (updatedServices: Microservice[], updatedDeps: Dependency[]) => void;
}

export const GraphCanvas: React.FC<GraphCanvasProps> = ({ 
  services: initialServices, 
  dependencies: initialDeps,
  onSaveArchitecture 
}) => {
  const [services, setServices] = useState<Microservice[]>(initialServices);
  const [dependencies, setDependencies] = useState<Dependency[]>(initialDeps);
  const [selectedService, setSelectedService] = useState<Microservice | null>(null);
  
  // Keep track of coordinates of each service node for rendering
  const [positions, setPositions] = useState<Record<string, { x: number; y: number }>>({});
  const [draggingNode, setDraggingNode] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  // Reset local state if props change (e.g. new file uploaded)
  useEffect(() => {
    setServices(initialServices);
    setDependencies(initialDeps);
    
    // Position services in a nice circular/oval layout by default
    const newPositions: Record<string, { x: number; y: number }> = {};
    const radiusX = 300;
    const radiusY = 160;
    const centerX = 400;
    const centerY = 240;
    
    initialServices.forEach((service, index) => {
      const angle = (index / initialServices.length) * 2 * Math.PI;
      newPositions[service.id] = {
        x: centerX + radiusX * Math.cos(angle) - 90,
        y: centerY + radiusY * Math.sin(angle) - 45
      };
    });
    setPositions(newPositions);
    setSelectedService(null);
  }, [initialServices, initialDeps]);

  // Handle Dragging Nodes
  const handleMouseDown = (serviceId: string, e: React.MouseEvent) => {
    e.preventDefault();
    setDraggingNode(serviceId);
    const pos = positions[serviceId] || { x: 100, y: 100 };
    setDragOffset({
      x: e.clientX - pos.x,
      y: e.clientY - pos.y
    });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (draggingNode) {
      setPositions(prev => ({
        ...prev,
        [draggingNode]: {
          x: e.clientX - dragOffset.x,
          y: e.clientY - dragOffset.y
        }
      }));
    }
  };

  const handleMouseUp = () => {
    setDraggingNode(null);
  };

  // Node customization updates
  const handleUpdateServiceName = (id: string, newName: string) => {
    const updated = services.map(s => s.id === id ? { ...s, name: newName } : s);
    setServices(updated);
    if (selectedService?.id === id) {
      setSelectedService(prev => prev ? { ...prev, name: newName } : null);
    }
  };

  const handleUpdateServiceDescription = (id: string, newDesc: string) => {
    const updated = services.map(s => s.id === id ? { ...s, description: newDesc } : s);
    setServices(updated);
    if (selectedService?.id === id) {
      setSelectedService(prev => prev ? { ...prev, description: newDesc } : null);
    }
  };

  const handleUpdateDatabase = (id: string, db: string, dbReasoning: string) => {
    const updated = services.map(s => s.id === id ? { ...s, database: db, database_reasoning: dbReasoning } : s);
    setServices(updated);
    if (selectedService?.id === id) {
      setSelectedService(prev => prev ? { ...prev, database: db, database_reasoning: dbReasoning } : null);
    }
  };

  // API Endpoint CRUD
  const handleAddApi = (serviceId: string) => {
    const newApi: ApiEndpoint = {
      path: "/api/v1/new-endpoint",
      method: "GET",
      description: "Custom endpoint responsibilities."
    };
    const updated = services.map(s => {
      if (s.id === serviceId) {
        return { ...s, apis: [...s.apis, newApi] };
      }
      return s;
    });
    setServices(updated);
    const service = updated.find(s => s.id === serviceId);
    if (service) setSelectedService(service);
  };

  const handleRemoveApi = (serviceId: string, index: number) => {
    const updated = services.map(s => {
      if (s.id === serviceId) {
        const filteredApis = s.apis.filter((_, i) => i !== index);
        return { ...s, apis: filteredApis };
      }
      return s;
    });
    setServices(updated);
    const service = updated.find(s => s.id === serviceId);
    if (service) setSelectedService(service);
  };

  const handleUpdateApi = (serviceId: string, index: number, field: keyof ApiEndpoint, value: string) => {
    const updated = services.map(s => {
      if (s.id === serviceId) {
        const newApis = [...s.apis];
        newApis[index] = { ...newApis[index], [field]: value };
        return { ...s, apis: newApis };
      }
      return s;
    });
    setServices(updated);
    const service = updated.find(s => s.id === serviceId);
    if (service) setSelectedService(service);
  };

  // Add Service Node Dynamically
  const handleAddServiceNode = () => {
    const rawId = `custom-service-${Date.now()}`;
    const newService: Microservice = {
      id: rawId,
      name: "Custom Microservice",
      description: "User defined software domain service context.",
      domain: "Custom Bounded Context",
      database: "PostgreSQL",
      database_reasoning: "Selected based on schema modeling constraints.",
      apis: [
        { path: "/api/v1/health", method: "GET", description: "Default service health check." }
      ],
      scaling_recommendations: ["Distribute container replicas across server instances"]
    };
    
    setServices(prev => [...prev, newService]);
    setPositions(prev => ({
      ...prev,
      [rawId]: { x: 350 + Math.random() * 50, y: 200 + Math.random() * 50 }
    }));
  };

  const handleRemoveServiceNode = (serviceId: string) => {
    setServices(prev => prev.filter(s => s.id !== serviceId));
    setDependencies(prev => prev.filter(d => d.source !== serviceId && d.target !== serviceId));
    setSelectedService(null);
  };

  const triggerSave = () => {
    onSaveArchitecture(services, dependencies);
  };

  return (
    <div className="flex flex-col lg:flex-row gap-5 h-[620px]">
      {/* Topology Graph Canvas */}
      <div 
        className="flex-1 glass-panel rounded-3xl relative overflow-hidden border border-slate-800/80 bg-slate-950/20"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        {/* Canvas Toolbar Controls */}
        <div className="absolute top-4 left-4 z-10 flex gap-2">
          <button 
            onClick={handleAddServiceNode} 
            className="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 active:scale-95 transition-all text-xs font-semibold text-white rounded-xl shadow-lg border border-emerald-500/30"
          >
            <Plus size={14} />
            <span>Add Service</span>
          </button>
          <button 
            onClick={triggerSave}
            className="flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 active:scale-95 transition-all text-xs font-semibold text-white rounded-xl border border-slate-700/50 shadow-md"
          >
            <Save size={14} className="text-emerald-400" />
            <span>Save Changes</span>
          </button>
        </div>

        <div className="absolute top-4 right-4 text-[10px] text-slate-500 font-medium bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800/40">
          💡 Drag nodes to tidy layout. Click to inspect or modify APIs.
        </div>

        {/* SVG Drawing Layer for Arrows & Dependencies */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
          <defs>
            <marker 
              id="arrow" 
              viewBox="0 0 10 10" 
              refX="18" 
              refY="5" 
              markerWidth="6" 
              markerHeight="6" 
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#475569" />
            </marker>
            <marker 
              id="arrow-async" 
              viewBox="0 0 10 10" 
              refX="18" 
              refY="5" 
              markerWidth="6" 
              markerHeight="6" 
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#8b5cf6" />
            </marker>
          </defs>

          {/* Render Flow Connections */}
          {dependencies.map((dep, idx) => {
            const start = positions[dep.source];
            const end = positions[dep.target];
            if (!start || !end) return null;
            
            // Adjust offset to center of the cards
            const sX = start.x + 90;
            const sY = start.y + 45;
            const eX = end.x + 90;
            const eY = end.y + 45;
            
            const isAsync = dep.type === 'async';
            const strokeColor = isAsync ? "#8b5cf6" : "#334155";
            const markerId = isAsync ? "url(#arrow-async)" : "url(#arrow)";

            return (
              <g key={`dep-${idx}`}>
                <path
                  d={`M ${sX} ${sY} Q ${(sX + eX) / 2} ${(sY + eY) / 2 - 20}, ${eX} ${eY}`}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={2}
                  strokeDasharray={isAsync ? "5,5" : "none"}
                  markerEnd={markerId}
                  className="transition-all duration-300 opacity-60 hover:opacity-100"
                />
              </g>
            );
          })}
        </svg>

        {/* Floating Draggable Cards */}
        <div className="absolute inset-0 pointer-events-none">
          {services.map((service) => {
            const pos = positions[service.id] || { x: 100, y: 100 };
            const isSelected = selectedService?.id === service.id;
            
            return (
              <div
                key={service.id}
                style={{ 
                  left: `${pos.x}px`, 
                  top: `${pos.y}px`,
                  position: 'absolute'
                }}
                onMouseDown={(e) => handleMouseDown(service.id, e)}
                onClick={() => setSelectedService(service)}
                className={`w-[180px] h-[90px] rounded-2xl glass-panel p-3 flex flex-col justify-between pointer-events-auto node-draggable border select-none transition-shadow ${
                  isSelected 
                    ? 'border-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.25)]' 
                    : 'border-slate-800 hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[9px] font-bold text-slate-500 uppercase tracking-widest truncate max-w-[100px]">
                      {service.domain}
                    </span>
                    <Database size={10} className="text-emerald-400/80" />
                  </div>
                  <h5 className="text-xs font-bold text-white mt-1 leading-snug truncate">
                    {service.name}
                  </h5>
                </div>

                <div className="flex items-center justify-between border-t border-slate-800/80 pt-1.5 mt-1.5">
                  <span className="text-[9px] bg-slate-800/80 text-emerald-400 font-semibold px-1.5 py-0.5 rounded border border-slate-700/50">
                    {service.database.split(" ")[0]}
                  </span>
                  <div className="flex items-center gap-1.5">
                    {service.metadata?.cohesion_score !== undefined && (
                      <span
                        title={`Cohesion: ${Math.round(service.metadata.cohesion_score as number)}%`}
                        className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${
                          (service.metadata.cohesion_score as number) >= 70
                            ? 'bg-teal-500/10 text-teal-400 border-teal-500/20'
                            : (service.metadata.cohesion_score as number) >= 40
                            ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
                            : 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                        }`}
                      >
                        C:{Math.round(service.metadata.cohesion_score as number)}%
                      </span>
                    )}
                    <span className="text-[9px] text-slate-400 font-mono font-medium">
                      {service.apis.length} APIs
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Node Inspector Details Panel */}
      <div className="w-full lg:w-[360px] glass-panel rounded-3xl p-5 border border-slate-800/80 overflow-y-auto bg-slate-900/10 flex flex-col justify-between">
        {selectedService ? (
          <div className="flex-1 flex flex-col justify-between h-full">
            <div>
              {/* Header Info */}
              <div className="flex items-center justify-between pb-3.5 border-b border-slate-800/80 mb-4">
                <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Bounded Context Inspector</span>
                <div className="flex gap-1.5">
                  <button 
                    onClick={() => handleRemoveServiceNode(selectedService.id)} 
                    className="p-1.5 bg-rose-500/10 text-rose-400 rounded-lg hover:bg-rose-500/20"
                    title="Delete Service Node"
                  >
                    <Trash2 size={13} />
                  </button>
                  <button 
                    onClick={() => setSelectedService(null)} 
                    className="p-1.5 bg-slate-800 text-slate-400 rounded-lg hover:bg-slate-700"
                  >
                    <X size={13} />
                  </button>
                </div>
              </div>

              {/* Editable Name & Description */}
              <div className="space-y-3.5">
                <div>
                  <label className="text-[9px] font-bold uppercase tracking-wider text-slate-500 block mb-1">Service Name</label>
                  <input 
                    type="text" 
                    value={selectedService.name}
                    onChange={(e) => handleUpdateServiceName(selectedService.id, e.target.value)}
                    className="w-full bg-slate-900/80 border border-slate-850 text-xs font-semibold rounded-xl px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-[9px] font-bold uppercase tracking-wider text-slate-500 block mb-1">Bounded Context Domain</label>
                  <span className="text-xs bg-slate-950/40 border border-slate-850 block rounded-xl px-3 py-2 text-slate-400 font-medium">
                    {selectedService.domain}
                  </span>
                </div>
                {selectedService.metadata?.cohesion_score !== undefined && (() => {
                  const score = Math.round(selectedService.metadata.cohesion_score as number);
                  const color = score >= 70 ? 'bg-teal-500' : score >= 40 ? 'bg-yellow-500' : 'bg-rose-500';
                  const label = score >= 70 ? 'High Cohesion' : score >= 40 ? 'Moderate Cohesion' : 'Low Cohesion';
                  return (
                    <div>
                      <label className="text-[9px] font-bold uppercase tracking-wider text-slate-500 block mb-1">Domain Cohesion Score</label>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-slate-800/85 h-1.5 rounded-full overflow-hidden border border-slate-700/30">
                          <div className={`h-full ${color} rounded-full transition-all duration-700`} style={{ width: `${score}%` }} />
                        </div>
                        <span className="text-[10px] font-bold text-white w-8 text-right">{score}%</span>
                        <span className="text-[9px] text-slate-400">{label}</span>
                      </div>
                    </div>
                  );
                })()}
                <div>
                  <label className="text-[9px] font-bold uppercase tracking-wider text-slate-500 block mb-1">Core Responsibilities</label>
                  <textarea 
                    rows={2}
                    value={selectedService.description}
                    onChange={(e) => handleUpdateServiceDescription(selectedService.id, e.target.value)}
                    className="w-full bg-slate-900/80 border border-slate-850 text-xs rounded-xl px-3 py-2 text-slate-300 focus:outline-none focus:border-emerald-500 resize-none leading-relaxed"
                  />
                </div>
              </div>

              {/* Database suggestions */}
              <div className="mt-4 pt-3.5 border-t border-slate-800/60">
                <div className="flex items-center gap-1.5 text-xs font-bold text-white mb-2">
                  <Database size={13} className="text-emerald-400" />
                  <span>Database Recommendation</span>
                </div>
                <input 
                  type="text" 
                  value={selectedService.database}
                  onChange={(e) => handleUpdateDatabase(selectedService.id, e.target.value, selectedService.database_reasoning)}
                  className="w-full bg-slate-900/80 border border-slate-850 text-xs font-semibold rounded-xl px-3 py-2 text-emerald-300 focus:outline-none focus:border-emerald-500"
                />
                <p className="text-[10px] text-gray-400/90 mt-1.5 leading-relaxed italic bg-slate-950/20 p-2 rounded-lg border border-slate-900/30">
                  {selectedService.database_reasoning}
                </p>
              </div>

              {/* Endpoints listing */}
              <div className="mt-4 pt-3.5 border-t border-slate-800/60">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-white">
                    <Network size={13} className="text-indigo-400" />
                    <span>REST Endpoints</span>
                  </div>
                  <button 
                    onClick={() => handleAddApi(selectedService.id)}
                    className="p-1 bg-slate-800 hover:bg-slate-700 text-emerald-400 rounded-md border border-slate-700/50"
                  >
                    <Plus size={12} />
                  </button>
                </div>

                <div className="space-y-2 max-h-[160px] overflow-y-auto pr-1">
                  {selectedService.apis.map((api, idx) => (
                    <div key={idx} className="bg-slate-950/40 border border-slate-900 p-2.5 rounded-xl flex flex-col gap-1.5 relative group">
                      <div className="flex items-center gap-1.5">
                        <select 
                          value={api.method}
                          onChange={(e) => handleUpdateApi(selectedService.id, idx, "method", e.target.value)}
                          className="bg-slate-900 border border-slate-800 text-[10px] font-bold text-slate-300 rounded px-1.5 py-0.5 focus:outline-none focus:border-emerald-500"
                        >
                          {['GET', 'POST', 'PUT', 'DELETE'].map(m => (
                            <option key={m} value={m}>{m}</option>
                          ))}
                        </select>
                        <input 
                          type="text" 
                          value={api.path}
                          onChange={(e) => handleUpdateApi(selectedService.id, idx, "path", e.target.value)}
                          className="flex-1 bg-slate-900 border border-slate-800 text-[10px] font-mono text-white rounded px-2 py-0.5 focus:outline-none focus:border-emerald-500"
                        />
                        <button 
                          onClick={() => handleRemoveApi(selectedService.id, idx)}
                          className="text-slate-500 hover:text-rose-400"
                        >
                          <Trash2 size={11} />
                        </button>
                      </div>
                      <input 
                        type="text" 
                        value={api.description}
                        onChange={(e) => handleUpdateApi(selectedService.id, idx, "description", e.target.value)}
                        className="bg-transparent text-[9px] text-gray-400 w-full focus:outline-none border-b border-transparent focus:border-slate-800 py-0.5"
                        placeholder="Description"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center py-20">
            <Settings size={36} className="text-slate-700 animate-spin-slow mb-4" />
            <h5 className="text-sm font-bold text-slate-400">Context Panel Empty</h5>
            <p className="text-xs text-slate-500 mt-1.5 max-w-[220px] leading-relaxed">
              Select any microservice node on the topology flow map to inspect parameters, rename contexts, or define API endpoints.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
