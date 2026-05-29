import React, { useState } from 'react';
import { TraceabilityRow, RequirementSentence } from '../types';
import { ChevronDown, ChevronRight, FileText, Zap, AlertCircle } from 'lucide-react';

interface TraceabilityTableProps {
  rows: TraceabilityRow[];
  impactMap?: Record<string, string[]>;
}

export const TraceabilityTable: React.FC<TraceabilityTableProps> = ({ rows, impactMap = {} }) => {
  const [expanded, setExpanded] = useState<string | null>(null);
  const [impactTarget, setImpactTarget] = useState<string | null>(null);

  if (!rows || rows.length === 0) {
    return (
      <div className="text-center py-8 text-xs text-slate-500 italic">
        No traceability data available. Re-upload your requirements document to generate a matrix.
      </div>
    );
  }

  const confidenceColor = (c: number) => {
    if (c >= 60) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
    if (c >= 30) return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
    return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
  };

  const confidenceBarColor = (c: number) => {
    if (c >= 60) return 'bg-emerald-500';
    if (c >= 30) return 'bg-yellow-500';
    return 'bg-rose-500';
  };

  // Resolve service names from IDs for impact display
  const idToName: Record<string, string> = {};
  rows.forEach(r => { idToName[r.service_id] = r.service_name; });

  return (
    <div className="space-y-2">
      {/* Header */}
      <div className="grid grid-cols-[1fr_120px_1fr] gap-3 px-3 pb-1 border-b border-slate-800">
        <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">Microservice</span>
        <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500 text-center">Confidence</span>
        <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">Matched Keywords</span>
      </div>

      {rows.map((row) => {
        const isOpen = expanded === row.service_id;
        const confidenceVal = typeof row.confidence === 'number' ? row.confidence : 0;
        const isInferred = row.inferred === true;
        return (
          <div
            key={row.service_id}
            className={`rounded-xl border overflow-hidden ${isInferred ? 'border-amber-500/30 bg-amber-500/3' : 'border-slate-800/80 bg-slate-950/20'}`}
          >
            {/* Collapsed row */}
            <button
              onClick={() => setExpanded(isOpen ? null : row.service_id)}
              className="w-full grid grid-cols-[1fr_120px_1fr] gap-3 px-3 py-2.5 text-left hover:bg-slate-900/40 transition-colors"
            >
              <div className="flex items-center gap-2 min-w-0">
                {isOpen
                  ? <ChevronDown size={12} className="text-emerald-400 flex-shrink-0" />
                  : <ChevronRight size={12} className="text-slate-500 flex-shrink-0" />
                }
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    <p className="text-xs font-semibold text-white truncate">{row.service_name}</p>
                    {isInferred && (
                      <span className="text-[7px] font-bold uppercase tracking-wider px-1 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/20 flex-shrink-0">
                        inferred
                      </span>
                    )}
                  </div>
                  <p className="text-[9px] text-slate-500 truncate">{row.domain}</p>
                </div>
              </div>

              <div className="flex flex-col items-center justify-center gap-1">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${confidenceColor(confidenceVal)}`}>
                  {confidenceVal.toFixed(1)}%
                </span>
                <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${confidenceBarColor(confidenceVal)}`}
                    style={{ width: `${Math.min(100, confidenceVal)}%` }}
                  />
                </div>
              </div>

              <div className="flex items-center flex-wrap gap-1 min-w-0 overflow-hidden">
                {(row.matched_keywords || []).slice(0, 4).map((kw) => (
                  <span key={kw} className="text-[9px] bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-1.5 py-0.5 rounded font-mono">
                    {kw}
                  </span>
                ))}
                {(row.matched_keywords || []).length > 4 && (
                  <span className="text-[9px] text-slate-500">+{row.matched_keywords.length - 4} more</span>
                )}
              </div>
            </button>

            {/* Expanded panel */}
            {isOpen && (
              <div className="px-4 pb-4 border-t border-slate-800/60 pt-3 space-y-3">

                {/* Inferred warning */}
                {isInferred && (
                  <div className="flex items-start gap-2 bg-amber-500/8 border border-amber-500/25 rounded-lg px-3 py-2">
                    <AlertCircle size={11} className="text-amber-400 mt-0.5 flex-shrink-0" />
                    <p className="text-[10px] text-amber-300 leading-relaxed">
                      <strong>Inferred, not stated.</strong> Fewer than 2 FR-IDs explicitly justify this boundary.
                      It was generated from keyword frequency alone — verify before implementing.
                    </p>
                  </div>
                )}

                {/* DDD boundary justification */}
                {row.boundary_justification && (
                  <div className="flex items-start gap-2 bg-indigo-500/5 border border-indigo-500/20 rounded-lg px-3 py-2">
                    <span className="text-[9px] font-bold uppercase tracking-widest text-indigo-400 mt-0.5 flex-shrink-0">DDD</span>
                    <p className="text-[10px] text-indigo-300 leading-relaxed">{row.boundary_justification}</p>
                  </div>
                )}

                {/* FR-IDs that justify this service */}
                {row.justified_fr_ids && row.justified_fr_ids.length > 0 && (
                  <div>
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">
                        Justifying FR-IDs ({row.justified_fr_ids.length})
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {row.justified_fr_ids.map((frId) => {
                        const affectedServices = impactMap[frId] ?? [];
                        return (
                          <button
                            key={frId}
                            onClick={() => setImpactTarget(impactTarget === frId ? null : frId)}
                            className={`group relative text-[9px] font-mono font-bold px-2 py-0.5 rounded border transition-colors ${
                              impactTarget === frId
                                ? 'bg-teal-500/20 text-teal-300 border-teal-500/40'
                                : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20'
                            }`}
                          >
                            {frId}
                            {affectedServices.length > 1 && (
                              <span className="ml-1 text-[7px] text-emerald-600">
                                ×{affectedServices.length}
                              </span>
                            )}
                          </button>
                        );
                      })}
                    </div>

                    {/* Impact analysis panel */}
                    {impactTarget && (impactMap[impactTarget] ?? []).length > 0 && (
                      <div className="mt-2 flex items-start gap-2 bg-teal-500/5 border border-teal-500/20 rounded-lg px-3 py-2">
                        <Zap size={10} className="text-teal-400 mt-0.5 flex-shrink-0" />
                        <div>
                          <p className="text-[9px] font-bold text-teal-300 mb-1">
                            Impact of changing {impactTarget}:
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {(impactMap[impactTarget] ?? []).map((svcId) => (
                              <span key={svcId} className="text-[9px] font-mono bg-teal-500/10 text-teal-300 border border-teal-500/20 px-1.5 py-0.5 rounded">
                                {idToName[svcId] ?? svcId}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Requirement sentences with line + FR-ID provenance */}
                <div>
                  <div className="flex items-center gap-1.5 mb-2">
                    <FileText size={11} className="text-slate-400" />
                    <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">
                      Requirement Sentences ({row.requirement_sentences.length})
                    </span>
                  </div>
                  {row.requirement_sentences.length > 0 ? (
                    row.requirement_sentences.map((sent: RequirementSentence, idx: number) => (
                      <div key={idx} className="flex gap-2 items-start mb-2">
                        <div className="flex flex-col items-center gap-0.5 flex-shrink-0 pt-0.5">
                          <span className="text-[9px] font-bold text-slate-600">R{idx + 1}</span>
                          <span className="text-[8px] font-mono text-slate-700">L{sent.line}</span>
                        </div>
                        <div className="min-w-0 flex-1">
                          {sent.fr_ids && sent.fr_ids.length > 0 && (
                            <div className="flex flex-wrap gap-1 mb-1">
                              {sent.fr_ids.map((id: string) => (
                                <span key={id} className="text-[8px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 px-1.5 py-0.5 rounded">
                                  {id}
                                </span>
                              ))}
                            </div>
                          )}
                          <p className="text-[10px] text-slate-300 leading-relaxed italic bg-slate-900/60 px-2.5 py-1.5 rounded-lg border border-slate-800/60">
                            "{sent.text}"
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-[10px] text-slate-500 italic">
                      No explicit requirement sentences matched. Service detected via semantic domain patterns.
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
