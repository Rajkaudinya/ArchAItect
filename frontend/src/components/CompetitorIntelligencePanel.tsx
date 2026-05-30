import { useState } from 'react';
import { Building2, ExternalLink, Radar, RefreshCw, Search } from 'lucide-react';
import { CompetitorIntelligence } from '../types';

interface CompetitorIntelligencePanelProps {
  intelligence: CompetitorIntelligence | null;
  isResearching: boolean;
  error: string;
  onResearch: (appType?: string) => void;
}

function extractUrl(sourceHint: string) {
  return sourceHint.match(/https?:\/\/[^\s)]+/)?.[0];
}

export function CompetitorIntelligencePanel({
  intelligence,
  isResearching,
  error,
  onResearch,
}: CompetitorIntelligencePanelProps) {
  const [appType, setAppType] = useState('');
  const unavailable = intelligence?.competitor === 'Unavailable';

  return (
    <div className="space-y-5">
      <div className="glass-panel bracket-accent p-5 rounded-2xl border-[var(--border-light)]">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5">
          <div className="max-w-2xl">
            <p className="section-label mb-1">Agent 4 / Web-Grounded Research</p>
            <h4 className="font-display text-base font-bold text-[var(--text-primary)]">
              Competitor Intelligence
            </h4>
            <p className="text-xs text-[var(--text-secondary)] mt-1 leading-relaxed">
              Compare your proposed services with one real company using public engineering blogs,
              conference talks, and technical documentation.
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-2 w-full lg:w-auto">
            <input
              value={appType}
              onChange={event => setAppType(event.target.value)}
              placeholder="Optional domain, e.g. food delivery"
              className="field-input px-3 py-2 text-xs min-w-[250px]"
              disabled={isResearching}
            />
            <button
              onClick={() => onResearch(appType.trim() || undefined)}
              disabled={isResearching}
              className="btn-cyan px-4 py-2 rounded-xl text-xs flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-wait"
            >
              {isResearching ? <RefreshCw size={13} className="animate-spin" /> : <Search size={13} />}
              {isResearching ? 'Researching...' : intelligence ? 'Research Again' : 'Run Agent 4'}
            </button>
          </div>
        </div>
      </div>

      {isResearching && (
        <div className="glass-panel p-8 rounded-2xl border-[var(--border-light)] text-center">
          <Radar size={28} className="animate-spin-slow mx-auto mb-4" style={{ color: 'var(--cyan-deep)' }} />
          <p className="font-display text-sm font-bold text-[var(--text-primary)]">Searching public architecture sources</p>
          <p className="text-xs text-[var(--text-secondary)] mt-2">Groq Compound Mini is finding evidence-backed systems and comparison points.</p>
        </div>
      )}

      {error && (
        <div className="glass-panel glass-coral p-4 rounded-2xl text-xs text-[var(--coral-deep)]">
          {error}
        </div>
      )}

      {intelligence && !isResearching && (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
          <div className="xl:col-span-2 glass-panel p-5 rounded-2xl border-[var(--border-light)]">
            <div className="flex items-start justify-between gap-4 pb-4 mb-4 border-b border-[var(--border-light)]">
              <div>
                <p className="section-label mb-1">Comparable Company</p>
                <h4 className="font-display text-xl font-bold text-[var(--text-primary)] flex items-center gap-2">
                  <Building2 size={18} style={{ color: 'var(--cyan-deep)' }} />
                  {intelligence.competitor}
                </h4>
                <p className="text-xs text-[var(--text-secondary)] mt-2 leading-relaxed">
                  {intelligence.why_relevant}
                </p>
              </div>
              <span className={unavailable ? 'badge-coral text-[9px] px-2.5 py-1 rounded-lg' : 'badge-emerald text-[9px] px-2.5 py-1 rounded-lg'}>
                {unavailable ? 'UNAVAILABLE' : 'WEB GROUNDED'}
              </span>
            </div>

            {intelligence.known_services.length > 0 ? (
              <div className="space-y-3">
                {intelligence.known_services.map((service, index) => {
                  const sourceUrl = extractUrl(service.source_hint);
                  return (
                    <div key={`${service.name}-${index}`} className="p-4 rounded-xl border border-[var(--border-light)] bg-white/55">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h5 className="text-sm font-bold text-[var(--text-primary)]">{service.name}</h5>
                          <p className="text-xs text-[var(--text-secondary)] mt-1 leading-relaxed">{service.purpose}</p>
                        </div>
                        {sourceUrl && (
                          <a
                            href={sourceUrl}
                            target="_blank"
                            rel="noreferrer"
                            className="badge-cyan text-[9px] px-2 py-1 rounded-lg flex items-center gap-1 flex-shrink-0"
                          >
                            Source <ExternalLink size={10} />
                          </a>
                        )}
                      </div>
                      <p className="font-mono-custom text-[10px] text-[var(--text-muted)] mt-3 break-words">
                        {service.source_hint}
                      </p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-xs text-[var(--text-muted)] italic">No public service details were returned.</p>
            )}
          </div>

          <div className="glass-panel p-5 rounded-2xl border-[var(--border-light)]">
            <p className="section-label mb-1">Architecture Review</p>
            <h4 className="font-display text-base font-bold text-[var(--text-primary)] mb-4">Actionable Insights</h4>
            {intelligence.insights.length > 0 ? (
              <ol className="space-y-3">
                {intelligence.insights.map((insight, index) => (
                  <li key={index} className="flex gap-3 text-xs text-[var(--text-secondary)] leading-relaxed">
                    <span className="badge-violet w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 font-bold">
                      {index + 1}
                    </span>
                    <span>{insight}</span>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="text-xs text-[var(--text-muted)] italic">No comparison insights are available.</p>
            )}
          </div>
        </div>
      )}

      {!intelligence && !isResearching && (
        <div className="glass-panel p-8 rounded-2xl border-[var(--border-light)] text-center">
          <Radar size={28} className="mx-auto mb-4" style={{ color: 'var(--cyan-deep)' }} />
          <p className="font-display text-sm font-bold text-[var(--text-primary)]">Ready for a real-world comparison</p>
          <p className="text-xs text-[var(--text-secondary)] mt-2">Run Agent 4 after your architecture has been generated.</p>
        </div>
      )}
    </div>
  );
}
