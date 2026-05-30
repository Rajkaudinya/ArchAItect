import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { GitBranch, Copy, Check, Code, Eye } from 'lucide-react';

interface FlowDiagramProps { mermaid: string; }

let mermaidInitialized = false;
let diagramCounter = 0;

export const FlowDiagram: React.FC<FlowDiagramProps> = ({ mermaid: mermaidCode }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false);
  const [view, setView] = useState<'diagram' | 'code'>('diagram');
  const [renderError, setRenderError] = useState<string | null>(null);
  const [svgContent, setSvgContent] = useState<string>('');
  const [isRendering, setIsRendering] = useState(false);

  // Initialize Mermaid once
  useEffect(() => {
    if (!mermaidInitialized) {
      mermaid.initialize({
        startOnLoad: false,
        theme: 'dark',
        themeVariables: {
          background: '#0f172a',
          primaryColor: '#1e293b',
          primaryTextColor: '#e2e8f0',
          primaryBorderColor: '#334155',
          lineColor: '#64748b',
          secondaryColor: '#1e293b',
          tertiaryColor: '#0f172a',
          edgeLabelBackground: '#1e293b',
          fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
          fontSize: '13px',
          nodeBorder: '#4ade80',
          clusterBkg: '#1e293b',
          titleColor: '#94a3b8',
          mainBkg: '#1e293b',
          nodeTextColor: '#e2e8f0',
          activationBorderColor: '#4ade80',
          activationBkgColor: '#1e293b',
          signalColor: '#94a3b8',
          signalTextColor: '#e2e8f0',
        },
        flowchart: {
          curve: 'basis',
          padding: 20,
          htmlLabels: true,
        },
        securityLevel: 'loose',
      });
      mermaidInitialized = true;
    }
  }, []); 

  useEffect(() => {
    if (!mermaidCode || mermaidCode.trim().length < 20) return;
    if (view !== 'diagram') return;
    let cancelled = false;
    const id = `mermaid-flow-${++diagramCounter}`;
    (async () => {
      try {
        setIsRendering(true);
        setRenderError(null);
        setSvgContent(''); // Clear previous content
        
        // Small delay to ensure Mermaid is fully initialized
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const { svg } = await mermaid.render(id, mermaidCode.trim());
        if (!cancelled) {
          setSvgContent(svg);
          setIsRendering(false);
        }
      } catch (err: any) {
        console.error('Mermaid render error:', err);
        if (!cancelled) {
          setRenderError(err?.message ?? 'Failed to render diagram');
          setSvgContent('');
          setIsRendering(false);
        }
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
      {view === 'diagram' ? (
        <div className="bg-slate-950/60 border border-slate-800/60 rounded-xl p-4 min-h-[180px] flex items-center justify-center overflow-auto">
          {isRendering ? (
            <div className="flex items-center gap-2 text-slate-500 text-xs">
              <div className="w-3 h-3 border border-teal-500 border-t-transparent rounded-full animate-spin" />
              Rendering diagram…
            </div>
          ) : renderError ? (
            <div className="text-center w-full">
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-3">
                <p className="text-red-400 text-xs font-semibold mb-1">⚠️ Diagram Render Error</p>
                <p className="text-red-300/70 text-[10px] font-mono">{renderError}</p>
              </div>
              <button
                onClick={() => setView('code')}
                className="text-[10px] text-slate-400 hover:text-white transition-colors underline"
              >
                View raw Mermaid code instead
              </button>
            </div>
          ) : svgContent ? (
            <div
              ref={containerRef}
              className="mermaid-output w-full overflow-auto"
              dangerouslySetInnerHTML={{ __html: svgContent }}
              style={{ maxWidth: '100%' }}
            />
          ) : (
            <div className="flex items-center gap-2 text-slate-500 text-xs">
              <div className="w-3 h-3 border border-teal-500 border-t-transparent rounded-full animate-spin" />
              Loading diagram…
            </div>
          )}
        </div>
      ) : (
        <pre className="text-[10px] font-mono text-slate-300 bg-slate-950/60 border border-slate-800/60 rounded-xl p-4 overflow-x-auto leading-relaxed whitespace-pre">
          {mermaidCode}
        </pre>
      )}
    </div>
  );
};