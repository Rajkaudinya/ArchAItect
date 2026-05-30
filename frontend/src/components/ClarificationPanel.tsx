import React, { useState } from 'react';
import { ClarificationQuestion } from '../types';
import { AlertTriangle, ChevronDown, ChevronRight, Hash, RefreshCw, CheckCircle } from 'lucide-react';

interface ClarificationPanelProps {
  questions: ClarificationQuestion[];
  onSubmitAnswers: (answers: { question: string; answer: string }[]) => void;
  isProcessing?: boolean;
}

const TYPE_META: Record<string, { label: string; css: string }> = {
  entity_no_actor:       { label: 'No Owner',     css: 'badge-gold'   },
  long_flow_no_boundary: { label: 'Tx Boundary',  css: 'badge-coral'  },
  capability_no_data:    { label: 'Missing Data', css: 'badge-violet' },
};

export const ClarificationPanel: React.FC<ClarificationPanelProps> = ({
  questions,
  onSubmitAnswers,
  isProcessing = false,
}) => {
  const [expanded,  setExpanded]  = useState<number | null>(0);
  const [answers,   setAnswers]   = useState<Record<number, string>>({});
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
    <div className="glass-panel glass-coral rounded-2xl overflow-hidden border-[var(--border-light)]">
      {/* Header */}
      <div className="flex items-center gap-3 px-5 py-4 border-b border-[rgba(255,92,92,0.12)]" style={{ background: 'rgba(255,92,92,0.03)' }}>
        <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'var(--coral-soft)', border: '1px solid rgba(255,92,92,0.2)' }}>
          <AlertTriangle size={14} style={{ color: 'var(--coral)' }} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="section-label mb-0.5" style={{ color: 'rgba(255,92,92,0.6)' }}>Action Required</p>
          <h4 className="font-display text-sm font-bold" style={{ color: 'var(--coral-deep)' }}>
            Requirement Clarifications
          </h4>
          <p className="text-[10px] mt-0.5 font-light hidden sm:block" style={{ color: 'rgba(255,92,92,0.55)' }}>
            Answer ambiguities then click <strong style={{ color: 'var(--coral-deep)' }}>Confirm & Rebuild</strong> to regenerate the architecture.
          </p>
        </div>
        <span className="badge-coral text-[9px] px-2.5 py-1 rounded-xl font-mono-custom flex-shrink-0">
          {answeredCount}/{questions.length}
        </span>
      </div>

      {/* Questions */}
      <div className="divide-y divide-[rgba(255,92,92,0.08)]">
        {questions.map((q, idx) => {
          const meta   = TYPE_META[q.type] ?? { label: q.type, css: 'badge-cyan' };
          const isOpen = expanded === idx;
          const hasAns = (answers[idx] ?? '').trim().length > 0;

          return (
            <div key={idx}>
              <button
                onClick={() => setExpanded(isOpen ? null : idx)}
                className="w-full flex items-start gap-3 px-5 py-3.5 text-left transition-colors hover:bg-[rgba(255,92,92,0.02)]"
              >
                <span className="mt-0.5" style={{ color: isOpen ? 'var(--coral)' : 'var(--text-muted)' }}>
                  {isOpen ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                    <span className={`text-[8px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${meta.css}`}>
                      {meta.label}
                    </span>
                    <span className="flex items-center gap-0.5 font-mono-custom text-[8px] text-[var(--text-muted)]">
                      <Hash size={7} />L{q.line}
                    </span>
                    {hasAns && (
                      <span className="badge-emerald text-[8px] px-1.5 py-0.5 rounded-full ml-auto flex items-center gap-1">
                        <CheckCircle size={8} /> Answered
                      </span>
                    )}
                  </div>
                  <p className="text-xs font-semibold text-[var(--text-primary)] leading-relaxed">{q.question}</p>
                </div>
              </button>

              {isOpen && (
                <div className="px-10 pb-5 space-y-3" style={{ background: 'rgba(255,92,92,0.015)' }}>
                  {q.sentence && (
                    <blockquote className="font-mono-custom text-[10px] italic text-[var(--text-secondary)] p-3 rounded-xl leading-relaxed border border-[var(--border-light)]" style={{ background: 'rgba(240,244,248,0.8)' }}>
                      "{q.sentence}"
                    </blockquote>
                  )}
                  <div className="flex items-start gap-2">
                    <span className="section-label mt-0.5 flex-shrink-0">Impact:</span>
                    <p className="text-[10px] text-[var(--text-secondary)] leading-relaxed">{q.impact}</p>
                  </div>
                  <div className="space-y-1.5">
                    <label className="section-label" style={{ color: 'var(--cyan-deep)' }}>Your Answer</label>
                    <textarea
                      rows={2}
                      placeholder="Type your answer here — it will be used to refine the service breakdown..."
                      value={answers[idx] ?? ''}
                      onChange={e => setAnswers(prev => ({ ...prev, [idx]: e.target.value }))}
                      className="field-input w-full px-3 py-2 text-xs resize-none leading-relaxed"
                    />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div
        className="px-5 py-4 border-t border-[rgba(255,92,92,0.1)] flex items-center justify-between gap-4 flex-wrap"
        style={{ background: 'rgba(255,255,255,0.5)' }}
      >
        <p className="text-[10px] text-[var(--text-muted)]">
          Partial answers still improve architecture accuracy.
        </p>
        <button
          onClick={handleSubmit}
          disabled={isProcessing || submitted}
          className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold transition-all ${
            isProcessing || submitted
              ? 'bg-[var(--border-light)] text-[var(--text-muted)] cursor-not-allowed'
              : 'btn-cyan'
          }`}
        >
          {isProcessing ? (
            <>
              <div className="bar-loader h-4" style={{ gap: '2px' }}>
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="bar-loader-bar" style={{ width: '3px', animationDelay: `${i * 0.12}s` }} />
                ))}
              </div>
              Rebuilding...
            </>
          ) : submitted ? (
            <>
              <CheckCircle size={12} style={{ color: 'var(--emerald)' }} />
              Submitted
            </>
          ) : (
            <>
              <RefreshCw size={12} />
              Confirm & Rebuild Architecture
            </>
          )}
        </button>
      </div>
    </div>
  );
};