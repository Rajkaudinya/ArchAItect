import { useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge as RFEdge,
  MarkerType,
  ReactFlowProvider,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Maximize2, Minimize2 } from "lucide-react";
import ServiceNode from "./ServiceNode";
import type { Architecture } from "@/types/architecture";

const nodeTypes = { service: ServiceNode };

interface Props {
  arch: Architecture;
  selectedId: string | null;
  onSelect: (id: string) => void;
}

/** Layered auto-layout: roots on top, dependents below. */
function layout(arch: Architecture): Record<string, { x: number; y: number }> {
  const ids = arch.services.map((s) => s.id);
  const incoming: Record<string, number> = {};
  ids.forEach((id) => (incoming[id] = 0));
  arch.edges.forEach((e) => {
    if (e.to in incoming) incoming[e.to] += 1;
  });

  const layer: Record<string, number> = {};
  ids.forEach((id) => (layer[id] = incoming[id] === 0 ? 0 : 1));
  for (let pass = 0; pass < ids.length; pass++) {
    arch.edges.forEach((e) => {
      if (e.from in layer && e.to in layer) {
        layer[e.to] = Math.max(layer[e.to], layer[e.from] + 1);
      }
    });
  }

  const byLayer: Record<number, string[]> = {};
  ids.forEach((id) => {
    const l = layer[id] ?? 0;
    (byLayer[l] ??= []).push(id);
  });

  const COL = 290;
  const ROW = 220;
  const pos: Record<string, { x: number; y: number }> = {};
  Object.keys(byLayer)
    .map(Number)
    .sort((a, b) => a - b)
    .forEach((l) => {
      const row = byLayer[l];
      const totalW = (row.length - 1) * COL;
      row.forEach((id, i) => {
        pos[id] = { x: i * COL - totalW / 2, y: l * ROW };
      });
    });
  return pos;
}

function Flow({ arch, selectedId, onSelect }: Props) {
  // Build initial nodes ONCE per architecture so dragging isn't reset on re-render.
  const initialNodes: Node[] = useMemo(() => {
    const pos = layout(arch);
    return arch.services.map((s) => ({
      id: s.id,
      type: "service",
      position: pos[s.id] ?? { x: 0, y: 0 },
      data: { service: s, selected: false, onSelect },
    }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [arch]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);

  // Reset nodes when a NEW architecture loads.
  useEffect(() => {
    setNodes(initialNodes);
  }, [initialNodes, setNodes]);

  // Reflect selection into node data without recreating positions.
  useEffect(() => {
    setNodes((nds) =>
      nds.map((n) => ({ ...n, data: { ...n.data, selected: n.id === selectedId } }))
    );
  }, [selectedId, setNodes]);

  const initialEdges: RFEdge[] = useMemo(
    () =>
      arch.edges.map((e, i) => {
        const isAsync = e.type === "async";
        const color = isAsync ? "var(--violet)" : "var(--cyan-dim)";
        return {
          id: `e-${i}`,
          source: e.from,
          target: e.to,
          animated: isAsync,
          data: { from: e.from, to: e.to },
          style: { stroke: color, strokeWidth: 1.5, strokeDasharray: isAsync ? "5 4" : undefined },
          markerEnd: { type: MarkerType.ArrowClosed, color, width: 14, height: 14 },
          label: e.protocol,
          labelStyle: { fill: "var(--ink-faint)", fontSize: 9, fontFamily: "JetBrains Mono" },
          labelBgStyle: { fill: "var(--bg)", fillOpacity: 0.85 },
        };
      }),
    [arch]
  );

  const [edges, setEdges] = useEdgesState(initialEdges);
  useEffect(() => setEdges(initialEdges), [initialEdges, setEdges]);

  // Highlight edges touching the selected node.
  useEffect(() => {
    setEdges((eds) =>
      eds.map((ed) => {
        const touched =
          selectedId &&
          ((ed.data as { from: string }).from === selectedId ||
            (ed.data as { to: string }).to === selectedId);
        return {
          ...ed,
          style: {
            ...ed.style,
            strokeWidth: touched ? 2.4 : 1.5,
            opacity: selectedId && !touched ? 0.22 : 0.9,
          },
        };
      })
    );
  }, [selectedId, setEdges]);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      nodeTypes={nodeTypes}
      fitView
      fitViewOptions={{ padding: 0.25 }}
      minZoom={0.25}
      maxZoom={1.8}
      nodesDraggable
      nodesConnectable={false}
      elementsSelectable
      proOptions={{ hideAttribution: true }}
      onPaneClick={() => onSelect("")}
    >
      <Background variant={BackgroundVariant.Dots} gap={26} size={1} color="var(--line)" />
      <Controls showInteractive={false} position="bottom-left" />
    </ReactFlow>
  );
}

export default function ServiceMap({ arch, selectedId, onSelect }: Props) {
  const [fullscreen, setFullscreen] = useState(false);

  // Esc closes fullscreen.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setFullscreen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const Header = (
    <div className="flex items-center gap-2 border-b px-4 py-2.5" style={{ borderColor: "var(--line)" }}>
      <span className="font-mono text-[10px] tracking-wider" style={{ color: "var(--ink-faint)" }}>
        SERVICE MAP
      </span>
      <div className="ml-auto flex items-center gap-3 font-mono text-[9px]" style={{ color: "var(--ink-faint)" }}>
        <Legend color="var(--cyan-dim)" label="sync" />
        <Legend color="var(--violet)" label="async" dashed />
        <span className="hidden sm:inline">· drag nodes · click for detail</span>
        <button
          onClick={() => setFullscreen((f) => !f)}
          className="ml-1 flex items-center gap-1 rounded-md px-2 py-1 transition-colors"
          style={{ border: "1px solid var(--line)", color: "var(--ink-dim)", cursor: "pointer" }}
          title={fullscreen ? "Exit fullscreen (Esc)" : "Maximize map"}
        >
          {fullscreen ? <Minimize2 size={12} /> : <Maximize2 size={12} />}
          <span>{fullscreen ? "exit" : "expand"}</span>
        </button>
      </div>
    </div>
  );

  if (fullscreen) {
    return (
      <div className="fixed inset-0 z-[60] flex flex-col" style={{ background: "var(--bg)" }}>
        {Header}
        <div className="flex-1">
          <ReactFlowProvider>
            <Flow arch={arch} selectedId={selectedId} onSelect={onSelect} />
          </ReactFlowProvider>
        </div>
      </div>
    );
  }

  return (
    <div className="panel panel-glow overflow-hidden" style={{ height: 560 }}>
      {Header}
      <div style={{ height: "calc(100% - 41px)" }}>
        <ReactFlowProvider>
          <Flow arch={arch} selectedId={selectedId} onSelect={onSelect} />
        </ReactFlowProvider>
      </div>
    </div>
  );
}

function Legend({ color, label, dashed }: { color: string; label: string; dashed?: boolean }) {
  return (
    <span className="flex items-center gap-1.5">
      <span style={{ width: 16, height: 0, borderTop: `2px ${dashed ? "dashed" : "solid"} ${color}` }} />
      {label}
    </span>
  );
}
