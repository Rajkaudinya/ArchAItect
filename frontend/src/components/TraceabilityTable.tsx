import React, { useState } from 'react';
import { TraceabilityRow, RequirementSentence } from '../types';
import { ChevronDown, ChevronRight, FileText, Zap, AlertCircle } from 'lucide-react';

interface TraceabilityTableProps {
  rows: TraceabilityRow[];
  impactMap?: Record<string, string[]>;
}

export const TraceabilityTable: React.FC<TraceabilityTableProps> = ({ rows, impactMap = {} }) => {
  const [expanded,     setExpanded]    = useState<string | null>(null);
  const [impactTarget, setImpactTarget] = useState<string | null>(null);

  if (!rows || rows.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-3">
        <div className="bar-loader opacity-30">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="bar-loader-bar" />
          ))}
        </div>
        <p className="text-xs text-[var(--text-muted)] italic">
          No traceability data. Re-upload your requirements document to generate a matrix.
        </p>
      </div>
    );
  }

  const confidenceCss = (c: number) => {
    if (c >= 60) return 'badge-emerald';
    if (c >= 30) return 'badge-gold';
    return 'badge-coral';
  };

  const confidenceBar = (c: number) => {
    if (c >= 60) return 'var(--emerald)';
    if (c >= 30) return 'var(--gold)';
    return 'var(--coral)';
  };

  const idToName: Record<string, string> = {};
  rows.forEach(r => { idToName[r.service_id] = r.service_name; });

  return (
    <div className="space-y-1.5">
      {/* Header */}
      <div className="grid grid-cols-[1fr_110px_1fr] gap-3 px-4 pb-2.5 border-b border-[var(--border-light)]">
        <span className="section-label">Microservice</span>
        <span className="section-label text-center">Confidence</span>
        <span className="section-label">Matched Keywords</span>
      </div>

      {rows.map((row, rowIdx) => {
        const isOpen     = expanded === row.service_id;
        const confidence = typeof row.confidence === 'number' ? row.confidence : 0;
        const isInferred = row.inferred === true;

        return (
          <div
            key={row.service_id}
            className="rounded-xl border overflow-hidden transition-all stagger-in"
            style={{
              animationDelay: `${rowIdx * 0.04}s`,
              borderColor: isInferred ? 'rgba(247,183,49,0.3)' : 'var(--border-light)',
              background: isInferred ? 'rgba(247,183,49,0.03)' : 'rgba(255,255,255,0.5)',
            }}
          >
            <button
              onClick={() => setExpanded(isOpen ? null : row.service_id)}
              className="w-full grid grid-cols-[1fr_110px_1fr] gap-3 px-4 py-3 text-left transition-colors hover:bg-[var(--bg-deep)]"
            >
              {/* Service */}
              <div className="flex items-center gap-2 min-w-0">
                <span style={{ color: isOpen ? 'var(--cyan-deep)' : 'var(--text-muted)' }}>
                  {isOpen ? <ChevronDown size={11} /> : <ChevronRight size={11} />}
                </span>
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <p className="font-display text-xs font-bold text-[var(--text-primary)] truncate">{row.service_name}</p>
                    {isInferred && (
                      <span className="badge-gold font-mono-custom text-[7px] px-1 py-0.5 rounded">inferred</span>
                    )}
                  </div>
                  <p className="font-mono-custom text-[9px] text-[var(--text-muted)] truncate">{row.domain}</p>
                </div>
              </div>

              {/* Confidence */}
              <div className="flex flex-col items-center justify-center gap-1.5">
                <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${confidenceCss(confidence)}`}>
                  {confidence.toFixed(1)}%
                </span>
                <div className="w-full h-1 bg-[var(--border-light)] rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full metric-bar-fill"
                    style={{ width: `${Math.min(100, confidence)}%`, background: confidenceBar(confidence) }}
                  />
                </div>
              </div>

              {/* Keywords */}
              <div className="flex items-center flex-wrap gap-1 min-w-0 overflow-hidden">
                {(row.matched_keywords || []).slice(0, 4).map(kw => (
                  <span key={kw} className="badge-cyan font-mono-custom text-[8px] px-1.5 py-0.5 rounded-lg">
                    {kw}
                  </span>
                ))}
                {(row.matched_keywords || []).length > 4 && (
                  <span className="font-mono-custom text-[9px] text-[var(--text-muted)]">
                    +{row.matched_keywords.length - 4}
                  </span>
                )}
              </div>
            </button>

            {isOpen && (
              <div
                className="px-5 pb-5 pt-3 space-y-4 border-t border-[var(--border-light)]"
                style={{ background: 'rgba(240,249,255,0.5)' }}
              >
                {/* Inferred warning */}
                {isInferred && (
                  <div className="flex items-start gap-2 badge-gold border rounded-xl px-3 py-2.5">
                    <AlertCircle size={11} className="flex-shrink-0 mt-0.5" style={{ color: '#b45309' }} />
                    <p className="text-[10px] leading-relaxed" style={{ color: '#92400e' }}>
                      <strong>Inferred, not stated.</strong> Fewer than 2 FR-IDs explicitly justify this boundary. Verify before implementing.
                    </p>
                  </div>
                )}

                {/* DDD */}
                {row.boundary_justification && (
                  <div className="flex items-start gap-2 badge-cyan border rounded-xl px-3 py-2.5">
                    <span className="section-label mt-0.5 flex-shrink-0" style={{ color: 'var(--cyan-deep)' }}>DDD</span>
                    <p className="text-[10px] text-[var(--cyan-deep)] leading-relaxed">{row.boundary_justification}</p>
                  </div>
                )}

                {/* FR-IDs */}
                {row.justified_fr_ids && row.justified_fr_ids.length > 0 && (
                  <div>
                    <p className="section-label mb-2">Justifying FR-IDs ({row.justified_fr_ids.length})</p>
                    <div className="flex flex-wrap gap-1.5">
                      {row.justified_fr_ids.map(frId => {
                        const affected = impactMap[frId] ?? [];
                        return (
                          <button
                            key={frId}
                            onClick={() => setImpactTarget(impactTarget === frId ? null : frId)}
                            className={`font-mono-custom text-[9px] font-bold px-2 py-0.5 rounded-lg border transition-all ${
                              impactTarget === frId
                                ? 'badge-gold'
                                : 'badge-emerald hover:shadow-sm'
                            }`}
                          >
                            {frId}
                            {affected.length > 1 && (
                              <span className="ml-1 text-[7px] opacity-60">×{affected.length}</span>
                            )}
                          </button>
                        );
                      })}
                    </div>

                    {impactTarget && (impactMap[impactTarget] ?? []).length > 0 && (
                      <div className="mt-2 flex items-start gap-2 badge-cyan border rounded-xl px-3 py-2.5">
                        <Zap size={10} className="flex-shrink-0 mt-0.5" style={{ color: 'var(--cyan-deep)' }} />
                        <div>
                          <p className="font-mono-custom text-[9px] font-bold mb-1.5" style={{ color: 'var(--cyan-deep)' }}>
                            Impact of changing {impactTarget}:
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {(impactMap[impactTarget] ?? []).map(svcId => (
                              <span key={svcId} className="badge-cyan font-mono-custom text-[9px] px-1.5 py-0.5 rounded-lg">
                                {idToName[svcId] ?? svcId}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Requirement sentences */}
                <div>
                  <div className="flex items-center gap-1.5 mb-3">
                    <FileText size={10} className="text-[var(--text-muted)]" />
                    <p className="section-label">Requirement Sentences ({row.requirement_sentences.length})</p>
                  </div>
                  {row.requirement_sentences.length > 0 ? (
                    <div className="space-y-2">
                      {row.requirement_sentences.map((sent: RequirementSentence, idx: number) => (
                        <div key={idx} className="flex gap-3 items-start">
                          <div className="flex flex-col items-center gap-0.5 pt-0.5 flex-shrink-0">
                            <span className="font-mono-custom text-[8px] font-bold text-[var(--text-muted)]">R{idx + 1}</span>
                            <span className="font-mono-custom text-[7px] text-[var(--border-mid)]">L{sent.line}</span>
                          </div>
                          <div className="min-w-0 flex-1">
                            {sent.fr_ids && sent.fr_ids.length > 0 && (
                              <div className="flex flex-wrap gap-1 mb-1.5">
                                {sent.fr_ids.map((id: string) => (
                                  <span key={id} className="badge-gold font-mono-custom text-[8px] px-1.5 py-0.5 rounded">
                                    {id}
                                  </span>
                                ))}
                              </div>
                            )}
                            <p
                              className="font-mono-custom text-[10px] text-[var(--text-secondary)] leading-relaxed italic px-3 py-2 rounded-xl border border-[var(--border-light)]"
                              style={{ background: 'rgba(255,255,255,0.8)' }}
                            >
                              "{sent.text}"
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="font-mono-custom text-[10px] text-[var(--text-muted)] italic">
                      No explicit sentences matched — service detected via semantic domain patterns.
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