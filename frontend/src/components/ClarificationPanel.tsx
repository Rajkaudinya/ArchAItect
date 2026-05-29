import React, { useState } from 'react';
import { ClarificationQuestion } from '../types';
import { AlertTriangle, ChevronDown, ChevronRight, Hash, RefreshCw, CheckCircle } from 'lucide-react';

interface ClarificationPanelProps {
  questions: ClarificationQuestion[];
  onSubmitAnswers: (answers: { question: string; answer: string }[]) => void;
  isProcessing?: boolean;
}

const TYPE_META: Record<string, { label: string; color: string }> = {
  entity_no_actor:       { label: 'No Owner',       color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
  long_flow_no_boundary: { label: 'Tx Boundary',    color: 'text-rose-400  bg-rose-500/10  border-rose-500/20'  },
  capability_no_data:    { label: 'Missing Data',   color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
};

export const ClarificationPanel: React.FC<ClarificationPanelProps> = ({
  questions,
  onSubmitAnswers,
  isProcessing = false,
}) => {
  const [expanded, setExpanded]   = useState<number | null>(0);
  const [answers,  setAnswers]    = useState<Record<number, string>>({});
  const [submitted, setSubmitted] = useState(false);

  if (!questions || questions.length === 0) return null;

  const answeredCount = Object.values(answers).filter(v => v.trim()).length;

  const handleSubmit = () => {
    const payload = questions.map((q, idx) => ({
      question: q.question,
      answer:   answers[idx] ?? '',
    }));
    setSubmitted(true);
    onSubmitAnswers(payload);
  };

  return (
    <div className="glass-panel rounded-2xl border border-amber-500/20 overflow-hidden">
      {/* ── Header ────────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-3 px-5 py-3.5 border-b border-amber-500/15 bg-amber-500/3">
        <AlertTriangle size={14} className="text-amber-400 flex-shrink-0" />
        <div className="flex-1">
          <h4 className="text-sm font-extrabold uppercase tracking-widest text-amber-300">
            Requirement Clarifications Needed
          </h4>
          <p className="text-[10px] text-amber-400/60 mt-0.5 font-light">
            Answer these ambiguities, then click <strong className="text-amber-300">Confirm &amp; Rebuild</strong> to
            regenerate the microservice architecture with your context.
          </p>
        </div>
        <span className="text-[10px] font-mono font-bold bg-amber-500/15 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded">
          {answeredCount}/{questions.length} ANSWERED
        </span>
      </div>

      {/* ── Questions ─────────────────────────────────────────────────────── */}
      <div className="divide-y divide-amber-500/10">
        {questions.map((q, idx) => {
          const meta   = TYPE_META[q.type] ?? { label: q.type, color: 'text-slate-400 bg-slate-500/10 border-slate-500/20' };
          const isOpen = expanded === idx;
          const hasAnswer = (answers[idx] ?? '').trim().length > 0;

          return (
            <div key={idx} className="transition-colors">
              {/* Question row (clickable header) */}
              <button
                onClick={() => setExpanded(isOpen ? null : idx)}
                className="w-full flex items-start gap-3 px-5 py-3 text-left hover:bg-amber-500/5 transition-colors"
              >
                {isOpen
                  ? <ChevronDown  size={12} className="text-amber-400 mt-0.5 flex-shrink-0" />
                  : <ChevronRight size={12} className="text-slate-500 mt-0.5 flex-shrink-0" />}

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border ${meta.color}`}>
                      {meta.label}
                    </span>
                    <span className="flex items-center gap-0.5 text-[9px] font-mono text-slate-600">
                      <Hash size={8} />L{q.line}
                    </span>
                    {hasAnswer && (
                      <CheckCircle size={10} className="text-emerald-400 ml-auto" />
                    )}
                  </div>
                  <p className="text-xs font-semibold text-amber-200 leading-relaxed">
                    {q.question}
                  </p>
                </div>
              </button>

              {/* Expanded detail + answer box */}
              {isOpen && (
                <div className="px-10 pb-4 space-y-3">
                  {/* Source sentence */}
                  {q.sentence && (
                    <blockquote className="text-[10px] italic text-slate-400 bg-slate-950/40 border border-slate-800/60 rounded-lg px-3 py-2 font-mono leading-relaxed">
                      "{q.sentence}"
                    </blockquote>
                  )}

                  {/* Impact */}
                  <div className="flex items-start gap-1.5">
                    <span className="text-[9px] font-bold uppercase tracking-wider text-slate-500 mt-0.5 flex-shrink-0">
                      Impact:
                    </span>
                    <p className="text-[10px] text-slate-400 leading-relaxed">{q.impact}</p>
                  </div>

                  {/* Answer textarea */}
                  <div className="space-y-1">
                    <label className="text-[9px] font-bold uppercase tracking-wider text-teal-400">
                      Your Answer
                    </label>
                    <textarea
                      rows={2}
                      placeholder="Type your answer here — it will be used to refine the service breakdown..."
                      value={answers[idx] ?? ''}
                      onChange={e => setAnswers(prev => ({ ...prev, [idx]: e.target.value }))}
                      className="w-full bg-slate-900/80 border border-slate-700 focus:border-teal-500 focus:outline-none rounded-lg px-3 py-2 text-xs text-white placeholder-slate-600 resize-none transition-colors"
                    />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* ── Footer: Confirm & Rebuild button ──────────────────────────────── */}
      <div className="px-5 py-4 border-t border-amber-500/15 bg-slate-900/30 flex items-center justify-between gap-3">
        <p className="text-[10px] text-slate-500 leading-relaxed">
          You can skip questions — partial answers still improve accuracy.
        </p>
        <button
          onClick={handleSubmit}
          disabled={isProcessing || submitted}
          className={`flex items-center gap-2 px-5 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all border
            ${isProcessing || submitted
              ? 'bg-slate-800 text-slate-500 border-slate-700 cursor-not-allowed'
              : 'bg-teal-600 hover:bg-teal-500 active:scale-95 text-white border-teal-500/30 shadow-lg'
            }`}
        >
          {isProcessing ? (
            <>
              <div className="w-3 h-3 border border-teal-400 border-t-transparent rounded-full animate-spin" />
              Rebuilding...
            </>
          ) : submitted ? (
            <>
              <CheckCircle size={12} className="text-emerald-400" />
              Submitted
            </>
          ) : (
            <>
              <RefreshCw size={12} />
              Confirm &amp; Rebuild Architecture
            </>
          )}
        </button>
      </div>
    </div>
  );
};
