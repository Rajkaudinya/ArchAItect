import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { GitBranch, Copy, Check, Code, Eye } from 'lucide-react';

interface FlowDiagramProps { mermaid: string; }

mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  themeVariables: {
    background:           '#f0f4f8',
    primaryColor:         '#e0f9fc',
    primaryTextColor:     '#0a0f1e',
    primaryBorderColor:   '#00d4e8',
    lineColor:            '#00a8be',
    secondaryColor:       '#fff0f0',
    tertiaryColor:        '#f0f4f8',
    edgeLabelBackground:  '#ffffff',
    fontFamily:           'JetBrains Mono, monospace',
    fontSize:             '12px',
    nodeBorder:           '#00d4e8',
    clusterBkg:           '#e0f9fc',
    titleColor:           '#475569',
    mainBkg:              '#ffffff',
    nodeTextColor:        '#0a0f1e',
    activationBorderColor:'#ff5c5c',
    activationBkgColor:   '#fff0f0',
    signalColor:          '#94a3b8',
    signalTextColor:      '#0a0f1e',
  },
  flowchart: { curve: 'basis', padding: 20, htmlLabels: true },
  securityLevel: 'loose',
});

let diagramCounter = 0;

export const FlowDiagram: React.FC<FlowDiagramProps> = ({ mermaid: mermaidCode }) => {
  const containerRef  = useRef<HTMLDivElement>(null);
  const [copied, setCopied]         = useState(false);
  const [view, setView]             = useState<'diagram' | 'code'>('diagram');
  const [renderError, setRenderError] = useState<string | null>(null);
  const [svgContent, setSvgContent]   = useState<string>('');

  useEffect(() => {
    if (!mermaidCode || mermaidCode.trim().length < 20) return;
    if (view !== 'diagram') return;
    let cancelled = false;
    const id = `mermaid-flow-${++diagramCounter}`;
    (async () => {
      try {
        setRenderError(null);
        const { svg } = await mermaid.render(id, mermaidCode.trim());
        if (!cancelled) setSvgContent(svg);
      } catch (err: any) {
        if (!cancelled) { setRenderError(err?.message ?? 'Failed to render'); setSvgContent(''); }
      }
    })();
    return () => { cancelled = true; };
  }, [mermaidCode, view]);

  if (!mermaidCode || mermaidCode.trim().length < 20) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(mermaidCode).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const liveUrl = `https://mermaid.live/edit#base64:${btoa(unescape(encodeURIComponent(mermaidCode)))}`;

  return (
    <div className="glass-panel rounded-2xl overflow-hidden border-[var(--border-light)]">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border-light)]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[var(--cyan-soft)] border border-[var(--border-cyan)] flex items-center justify-center">
            <GitBranch size={14} style={{ color: 'var(--cyan-deep)' }} />
          </div>
          <div>
            <p className="section-label mb-0.5">AI Generated</p>
            <h4 className="font-display text-sm font-bold text-[var(--text-primary)]">High-Level User Journey</h4>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center border border-[var(--border-light)] rounded-xl overflow-hidden">
            {(['diagram', 'code'] as const).map(v => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-[9px] font-bold uppercase tracking-wider transition-colors ${
                  view === v
                    ? 'bg-[var(--ink)] text-white'
                    : 'bg-transparent text-[var(--text-muted)] hover:text-[var(--text-primary)]'
                }`}
              >
                {v === 'diagram' ? <Eye size={9} /> : <Code size={9} />}
                {v}
              </button>
            ))}
          </div>

          <a
            href={liveUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="badge-cyan font-mono-custom text-[9px] px-2.5 py-1 rounded-lg hover:shadow-md transition-shadow"
          >
            Mermaid Live ↗
          </a>

          <button
            onClick={handleCopy}
            className="btn-ghost flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[9px] font-bold uppercase tracking-wider"
          >
            {copied
              ? <><Check size={10} style={{ color: 'var(--emerald)' }} />Copied</>
              : <><Copy size={10} />Copy</>
            }
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-5">
        {view === 'diagram' ? (
          <div
            className="rounded-xl p-4 min-h-[200px] flex items-center justify-center overflow-auto border border-[var(--border-light)]"
            style={{ background: 'rgba(240,249,255,0.7)' }}
          >
            {renderError ? (
              <div className="text-center">
                <span className="badge-coral text-xs px-3 py-1.5 rounded-lg mb-3 inline-block">Render error</span>
                <pre className="font-mono-custom text-[10px] text-[var(--text-secondary)] text-left whitespace-pre overflow-x-auto">
                  {mermaidCode}
                </pre>
              </div>
            ) : svgContent ? (
              <div
                ref={containerRef}
                className="mermaid-output w-full overflow-auto"
                dangerouslySetInnerHTML={{ __html: svgContent }}
                style={{ maxWidth: '100%' }}
              />
            ) : (
              <div className="flex flex-col items-center gap-3">
                <div className="bar-loader">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <div key={i} className="bar-loader-bar" style={{ animationDelay: `${i * 0.1}s` }} />
                  ))}
                </div>
                <span className="font-mono-custom text-[10px] text-[var(--text-muted)] tracking-widest uppercase">
                  Rendering diagram…
                </span>
              </div>
            )}
          </div>
        ) : (
          <pre
            className="font-mono-custom text-[10px] text-[var(--text-secondary)] rounded-xl p-4 overflow-x-auto leading-relaxed whitespace-pre border border-[var(--border-light)]"
            style={{ background: 'rgba(240,244,248,0.8)' }}
          >
            {mermaidCode}
          </pre>
        )}
      </div>
    </div>
  );
};