import React, { useEffect, useRef, useState, useCallback } from 'react';
import mermaid from 'mermaid';
import { GitBranch, Copy, Check, Code, Eye, ZoomIn, ZoomOut, Maximize2 } from 'lucide-react';

interface FlowDiagramProps { mermaid: string; }

let mermaidInitialized = false;
let diagramCounter = 0;

const MIN_ZOOM = 0.2;
const MAX_ZOOM = 4;
const ZOOM_STEP = 0.25;

function sanitizeMermaid(code: string): string {
  return code
    .replace(/^```(?:mermaid)?\s*\n?/gm, '')
    .replace(/\n?```\s*$/gm, '')
    .replace(/-->\|([^|>]+)\|>/g, '-->|$1|')
    .replace(/-\.->\|([^|>]+)\|>/g, '-.->|$1|')
    .replace(/--\|([^|>]+)\|>/g, '-.->|$1|')
    .replace(/--\|>/g, '-.->');
}

export const FlowDiagram: React.FC<FlowDiagramProps> = ({ mermaid: mermaidCode }) => {
  const svgWrapRef  = useRef<HTMLDivElement>(null);
  const viewportRef = useRef<HTMLDivElement>(null);

  const [copied,      setCopied]      = useState(false);
  const [view,        setView]        = useState<'diagram' | 'code'>('diagram');
  const [renderError, setRenderError] = useState<string | null>(null);
  const [svgContent,  setSvgContent]  = useState<string>('');
  const [isRendering, setIsRendering] = useState(false);
  const [zoom,        setZoom]        = useState(1);
  const [pan,         setPan]         = useState({ x: 0, y: 0 });
  const [isDragging,  setIsDragging]  = useState(false);

  // Refs keep the latest values accessible inside DOM event handlers
  const zoomRef        = useRef(1);
  const panRef         = useRef({ x: 0, y: 0 });
  const isDraggingRef  = useRef(false);
  const dragStartRef   = useRef({ mouseX: 0, mouseY: 0, panX: 0, panY: 0 });

  useEffect(() => { zoomRef.current = zoom; },        [zoom]);
  useEffect(() => { panRef.current  = pan; },         [pan]);
  useEffect(() => { isDraggingRef.current = isDragging; }, [isDragging]);

  // ── Mermaid init ───────────────────────────────────────────────────────────
  useEffect(() => {
    if (mermaidInitialized) return;
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      themeVariables: {
        background:            '#0f172a',
        primaryColor:          '#1e293b',
        primaryTextColor:      '#e2e8f0',
        primaryBorderColor:    '#334155',
        lineColor:             '#64748b',
        secondaryColor:        '#1e293b',
        tertiaryColor:         '#0f172a',
        edgeLabelBackground:   '#1e293b',
        fontFamily:            'ui-monospace, SFMono-Regular, Menlo, monospace',
        fontSize:              '13px',
        nodeBorder:            '#4ade80',
        clusterBkg:            '#1e293b',
        titleColor:            '#94a3b8',
        mainBkg:               '#1e293b',
        nodeTextColor:         '#e2e8f0',
        activationBorderColor: '#4ade80',
        activationBkgColor:    '#1e293b',
        signalColor:           '#94a3b8',
        signalTextColor:       '#e2e8f0',
      },
      flowchart: { curve: 'basis', padding: 20, htmlLabels: true },
      securityLevel: 'loose',
    });
    mermaidInitialized = true;
  }, []);

  // ── Render diagram ─────────────────────────────────────────────────────────
  useEffect(() => {
    if (!mermaidCode || mermaidCode.trim().length < 20) return;
    if (view !== 'diagram') return;
    let cancelled = false;
    const id = `mermaid-flow-${++diagramCounter}`;
    (async () => {
      try {
        setIsRendering(true);
        setRenderError(null);
        setSvgContent('');
        setZoom(1);
        setPan({ x: 0, y: 0 });
        await new Promise(r => setTimeout(r, 100));
        const { svg } = await mermaid.render(id, sanitizeMermaid(mermaidCode.trim()));
        if (!cancelled) { setSvgContent(svg); setIsRendering(false); }
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

  // ── Auto-fit after SVG renders ─────────────────────────────────────────────
  useEffect(() => {
    if (!svgContent) return;
    requestAnimationFrame(() => {
      const vp  = viewportRef.current;
      const wrap = svgWrapRef.current;
      if (!vp || !wrap) return;
      const svg = wrap.querySelector('svg');
      if (!svg) return;
      const vw = vp.clientWidth;
      const vh = vp.clientHeight;
      const sw = svg.scrollWidth  || svg.getBoundingClientRect().width;
      const sh = svg.scrollHeight || svg.getBoundingClientRect().height;
      if (sw > 0 && sh > 0) {
        const fit = Math.max(MIN_ZOOM, Math.min(1, Math.min(vw / sw, vh / sh) * 0.9));
        setZoom(fit);
        zoomRef.current = fit;
        setPan({ x: 0, y: 0 });
        panRef.current = { x: 0, y: 0 };
      }
    });
  }, [svgContent]);

  // ── Wheel zoom (non-passive, zoom toward cursor) ───────────────────────────
  useEffect(() => {
    const vp = viewportRef.current;
    if (!vp) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const rect = vp.getBoundingClientRect();
      const cx   = e.clientX - rect.left;
      const cy   = e.clientY - rect.top;
      const vcx  = rect.width  / 2;
      const vcy  = rect.height / 2;
      const dx   = cx - vcx;
      const dy   = cy - vcy;
      const factor   = e.deltaY > 0 ? 0.9 : 1.1;
      const curZ     = zoomRef.current;
      const curPan   = panRef.current;
      const newZ     = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, curZ * factor));
      const ratio    = newZ / curZ;
      const newPan   = { x: dx + (curPan.x - dx) * ratio, y: dy + (curPan.y - dy) * ratio };
      setZoom(newZ);
      setPan(newPan);
      zoomRef.current = newZ;
      panRef.current  = newPan;
    };
    vp.addEventListener('wheel', onWheel, { passive: false });
    return () => vp.removeEventListener('wheel', onWheel);
  }, [svgContent]);

  // ── Drag-to-pan ────────────────────────────────────────────────────────────
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 0) return;
    e.preventDefault();
    isDraggingRef.current = true;
    setIsDragging(true);
    dragStartRef.current = {
      mouseX: e.clientX, mouseY: e.clientY,
      panX:   panRef.current.x, panY: panRef.current.y,
    };
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDraggingRef.current) return;
    const d = dragStartRef.current;
    const newPan = { x: d.panX + e.clientX - d.mouseX, y: d.panY + e.clientY - d.mouseY };
    setPan(newPan);
    panRef.current = newPan;
  }, []);

  const handleMouseUp = useCallback(() => {
    isDraggingRef.current = false;
    setIsDragging(false);
  }, []);

  // ── Zoom buttons ───────────────────────────────────────────────────────────
  const zoomIn  = useCallback(() => {
    const n = Math.min(MAX_ZOOM, parseFloat((zoomRef.current + ZOOM_STEP).toFixed(2)));
    setZoom(n); zoomRef.current = n;
  }, []);

  const zoomOut = useCallback(() => {
    const n = Math.max(MIN_ZOOM, parseFloat((zoomRef.current - ZOOM_STEP).toFixed(2)));
    setZoom(n); zoomRef.current = n;
  }, []);

  const resetView = useCallback(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    zoomRef.current = 1;
    panRef.current  = { x: 0, y: 0 };
  }, []);

  if (!mermaidCode || mermaidCode.trim().length < 20) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(mermaidCode).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const liveUrl = `https://mermaid.live/edit#base64:${btoa(unescape(encodeURIComponent(sanitizeMermaid(mermaidCode))))}`;

  const btnBase =
    'flex items-center justify-center w-6 h-6 rounded-lg transition-all duration-150 disabled:opacity-30 disabled:cursor-not-allowed';
  const btnActive =
    'hover:bg-[var(--cyan-soft)] hover:text-[var(--cyan-deep)] text-[var(--text-muted)]';

  return (
    <div className="glass-panel rounded-2xl overflow-hidden border-[var(--border-light)] w-full">

      {/* ── Header ── */}
      <div className="flex flex-wrap items-center justify-between gap-2 px-4 sm:px-5 py-3 sm:py-4 border-b border-[var(--border-light)]">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-[var(--cyan-soft)] border border-[var(--border-cyan)] flex items-center justify-center flex-shrink-0">
            <GitBranch size={14} style={{ color: 'var(--cyan-deep)' }} />
          </div>
          <div>
            <p className="section-label mb-0.5">AI Generated</p>
            <h4 className="font-display text-sm font-bold text-[var(--text-primary)]">High-Level User Journey</h4>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Diagram / Code toggle */}
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
              : <><Copy size={10} />Copy</>}
          </button>
        </div>
      </div>

      {/* ── Content ── */}
      {view === 'diagram' ? (
        <div className="relative">

          {/* Viewport */}
          <div
            ref={viewportRef}
            className="relative bg-slate-950/60 border border-slate-800/60 rounded-xl m-3 sm:m-4 overflow-hidden select-none"
            style={{
              height: 'clamp(280px, 55vw, 520px)',
              cursor: isDragging ? 'grabbing' : svgContent ? 'grab' : 'default',
            }}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >

            {/* Loading */}
            {isRendering && (
              <div className="absolute inset-0 flex items-center justify-center gap-2 text-slate-500 text-xs">
                <div className="w-3 h-3 border border-teal-500 border-t-transparent rounded-full animate-spin" />
                Rendering diagram…
              </div>
            )}

            {/* Error */}
            {renderError && (
              <div className="absolute inset-0 flex flex-col items-center justify-center p-4">
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-3 max-w-sm w-full">
                  <p className="text-red-400 text-xs font-semibold mb-1">Diagram Render Error</p>
                  <p className="text-red-300/70 text-[10px] font-mono break-words">{renderError}</p>
                </div>
                <button
                  onClick={() => setView('code')}
                  className="text-[10px] text-slate-400 hover:text-white transition-colors underline"
                >
                  View raw Mermaid code instead
                </button>
              </div>
            )}

            {/* Loading placeholder */}
            {!isRendering && !renderError && !svgContent && (
              <div className="absolute inset-0 flex items-center justify-center gap-2 text-slate-500 text-xs">
                <div className="w-3 h-3 border border-teal-500 border-t-transparent rounded-full animate-spin" />
                Loading diagram…
              </div>
            )}

            {/* SVG canvas — transformed layer */}
            {svgContent && (
              <div
                ref={svgWrapRef}
                className="mermaid-output absolute inset-0 flex items-center justify-center pointer-events-none"
                style={{
                  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                  transformOrigin: 'center center',
                  transition: isDragging ? 'none' : 'transform 0.08s ease-out',
                  width: '100%',
                  height: '100%',
                }}
                dangerouslySetInnerHTML={{ __html: svgContent }}
              />
            )}

            {/* ── Floating zoom controls ── */}
            {svgContent && (
              <div
                className="absolute bottom-3 right-3 z-20 flex items-center gap-0.5 rounded-xl px-1.5 py-1 border border-[var(--border-light)] shadow-[var(--shadow-md)] backdrop-blur-md"
                style={{ background: 'var(--glass-bg)' }}
              >
                <button
                  onClick={zoomOut}
                  disabled={zoom <= MIN_ZOOM}
                  title="Zoom out"
                  className={`${btnBase} ${btnActive}`}
                >
                  <ZoomOut size={12} />
                </button>

                <span
                  className="text-[9px] font-bold tabular-nums w-9 text-center select-none"
                  style={{ color: 'var(--cyan-deep)', fontFamily: 'ui-monospace, monospace' }}
                >
                  {Math.round(zoom * 100)}%
                </span>

                <button
                  onClick={zoomIn}
                  disabled={zoom >= MAX_ZOOM}
                  title="Zoom in"
                  className={`${btnBase} ${btnActive}`}
                >
                  <ZoomIn size={12} />
                </button>

                <div className="w-px h-3 mx-0.5" style={{ background: 'var(--border-mid)' }} />

                <button
                  onClick={resetView}
                  title="Reset view"
                  className={`${btnBase} ${btnActive}`}
                >
                  <Maximize2 size={11} />
                </button>
              </div>
            )}

            {/* Hint */}
            {svgContent && (
              <div
                className="absolute top-2 left-3 z-10 text-[8px] pointer-events-none select-none"
                style={{ color: 'var(--text-muted)', fontFamily: 'ui-monospace, monospace' }}
              >
                scroll to zoom · drag to pan
              </div>
            )}
          </div>
        </div>
      ) : (
        <pre className="text-[10px] font-mono text-slate-300 bg-slate-950/60 border border-slate-800/60 rounded-xl m-3 sm:m-4 p-4 overflow-x-auto leading-relaxed whitespace-pre">
          {mermaidCode}
        </pre>
      )}
    </div>
  );
};
