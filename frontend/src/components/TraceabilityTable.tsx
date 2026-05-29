import React, { useState } from 'react';
import { TraceabilityRow } from '../types';
import { ChevronDown, ChevronRight, FileText } from 'lucide-react';

interface TraceabilityTableProps {
  rows: TraceabilityRow[];
}

export const TraceabilityTable: React.FC<TraceabilityTableProps> = ({ rows }) => {
  const [expanded, setExpanded] = useState<string | null>(null);

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

  return (
    <div className="space-y-2">
      {/* Header row */}
      <div className="grid grid-cols-[1fr_120px_1fr] gap-3 px-3 pb-1 border-b border-slate-800">
        <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">Microservice</span>
        <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500 text-center">Confidence</span>
        <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">Matched Keywords</span>
      </div>

      {rows.map((row) => {
        const isOpen = expanded === row.service_id;
        const confidenceVal = typeof row.confidence === 'number' ? row.confidence : 0;
        return (
          <div key={row.service_id} className="rounded-xl border border-slate-800/80 bg-slate-950/20 overflow-hidden">
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
                  <p className="text-xs font-semibold text-white truncate">{row.service_name}</p>
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

            {/* Expanded: requirement sentences */}
            {isOpen && (
              <div className="px-4 pb-3 border-t border-slate-800/60 pt-2.5 space-y-2">
                <div className="flex items-center gap-1.5 mb-2">
                  <FileText size={11} className="text-slate-400" />
                  <span className="text-[9px] font-bold uppercase tracking-widest text-slate-500">
                    Requirement Sentences ({(row.requirement_sentences || []).length})
                  </span>
                </div>

                {/* All keywords expanded */}
                {(row.matched_keywords || []).length > 4 && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {row.matched_keywords.map((kw) => (
                      <span key={kw} className="text-[9px] bg-indigo-500/10 text-indigo-300 border border-indigo-500/20 px-1.5 py-0.5 rounded font-mono">
                        {kw}
                      </span>
                    ))}
                  </div>
                )}

                {(row.requirement_sentences || []).length > 0 ? (
                  row.requirement_sentences.map((sentence, idx) => {
                    const sentenceText = typeof sentence === 'string' ? sentence : String(sentence);
                    return (
                      <div key={idx} className="flex gap-2 items-start">
                        <span className="text-[9px] font-bold text-slate-600 mt-0.5 flex-shrink-0">R{idx + 1}</span>
                        <p className="text-[10px] text-slate-300 leading-relaxed italic bg-slate-900/60 px-2.5 py-1.5 rounded-lg border border-slate-800/60">
                          "{sentenceText}"
                        </p>
                      </div>
                    );
                  })
                ) : (
                  <p className="text-[10px] text-slate-500 italic">
                    No explicit requirement sentences matched. Service detected via semantic domain patterns.
                  </p>
                )}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
