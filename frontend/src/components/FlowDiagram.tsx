import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { GitBranch, Copy, Check, Code, Eye } from 'lucide-react';

interface FlowDiagramProps {
  mermaid: string;
}

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

let diagramCounter = 0;

export const FlowDiagram: React.FC<FlowDiagramProps> = ({ mermaid: mermaidCode }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false);
  const [view, setView] = useState<'diagram' | 'code'>('diagram');
  const [renderError, setRenderError] = useState<string | null>(null);
  const [svgContent, setSvgContent] = useState<string>('');

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
        if (!cancelled) {
          setRenderError(err?.message ?? 'Failed to render diagram');
          setSvgContent('');
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
    <div className="glass-panel p-5 rounded-2xl border border-slate-800">
      {/* Header */}
      <div className="flex items-center justify-between pb-3.5 border-b border-slate-800/60 mb-4">
        <div className="flex items-center gap-2">
          <GitBranch size={14} className="text-teal-400" />
          <div>
            <h4 className="text-sm font-extrabold uppercase tracking-widest text-white">
              High-Level User Journey
            </h4>
            <p className="text-[10px] text-slate-500 mt-0.5 font-light">
              AI-generated flow from extracted actors, verbs &amp; entities — verify before reviewing service boundaries.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* View toggle */}
          <div className="flex items-center bg-slate-800 border border-slate-700 rounded overflow-hidden">
            <button
              onClick={() => setView('diagram')}
              className={`flex items-center gap-1 px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider transition-colors ${
                view === 'diagram' ? 'bg-teal-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Eye size={9} /> Diagram
            </button>
            <button
              onClick={() => setView('code')}
              className={`flex items-center gap-1 px-2.5 py-1 text-[9px] font-bold uppercase tracking-wider transition-colors ${
                view === 'code' ? 'bg-teal-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              <Code size={9} /> Code
            </button>
          </div>

          <a
            href={liveUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[9px] font-bold uppercase tracking-wider text-teal-400 border border-teal-500/30 bg-teal-500/10 hover:bg-teal-500/20 px-2.5 py-1 rounded transition-colors"
          >
            Mermaid Live ↗
          </a>

          <button
            onClick={handleCopy}
            className="flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider text-slate-400 border border-slate-700 bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded transition-colors"
          >
            {copied ? <Check size={10} className="text-emerald-400" /> : <Copy size={10} />}
            {copied ? 'Copied' : 'Copy'}
          </button>
        </div>
      </div>

      {/* Content */}
      {view === 'diagram' ? (
        <div className="bg-slate-950/60 border border-slate-800/60 rounded-xl p-4 min-h-[180px] flex items-center justify-center overflow-auto">
          {renderError ? (
            <div className="text-center">
              <p className="text-red-400 text-xs mb-2">Render error — showing raw code instead</p>
              <pre className="text-[10px] font-mono text-slate-400 text-left whitespace-pre overflow-x-auto">
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
            <div className="flex items-center gap-2 text-slate-500 text-xs">
              <div className="w-3 h-3 border border-teal-500 border-t-transparent rounded-full animate-spin" />
              Rendering diagram…
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
