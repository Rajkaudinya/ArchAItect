import { Handle, Position } from "@xyflow/react";
import type { Service } from "@/types/architecture";

interface NodeData {
  service: Service;
  selected: boolean;
  onSelect: (id: string) => void;
}

// Pick an accent per data store so the map is readable at a glance.
function storeColor(store: string): string {
  const s = store.toLowerCase();
  if (s.includes("redis")) return "var(--rose)";
  if (s.includes("mongo") || s.includes("nosql")) return "var(--violet)";
  if (s.includes("postgres") || s.includes("sql")) return "var(--cyan)";
  return "var(--amber)";
}

export default function ServiceNode({ data }: { data: NodeData }) {
  const { service, selected, onSelect } = data;
  const accent = storeColor(service.data_store);

  return (
    <div
      onClick={() => onSelect(service.id)}
      className="group rounded-xl transition-all duration-200"
      style={{
        width: 230,
        background: "linear-gradient(180deg, var(--panel) 0%, var(--bg-soft) 100%)",
        border: `1px solid ${selected ? accent : "var(--line)"}`,
        boxShadow: selected
          ? `0 0 0 1px ${accent}, 0 0 36px -6px ${accent}`
          : "0 12px 30px -18px rgba(0,0,0,0.9)",
        overflow: "hidden",
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: "var(--line)", width: 7, height: 7, border: "none" }} />

      {/* top accent bar keyed to data store */}
      <div style={{ height: 3, background: `linear-gradient(90deg, ${accent}, transparent)` }} />

      <div className="flex items-center gap-2 px-3.5 pt-2.5">
        <span className="h-2 w-2 rounded-full" style={{ background: accent, boxShadow: `0 0 8px ${accent}` }} />
        <span className="font-mono text-[10px] tracking-wider" style={{ color: "var(--ink-faint)" }}>
          {service.bounded_context.toUpperCase()}
        </span>
      </div>

      <div className="px-3.5 pb-1 pt-1.5">
        <div className="text-[15px] font-semibold leading-tight" style={{ color: "var(--ink)" }}>
          {service.name}
        </div>
      </div>

      <div className="px-3.5 pb-3 pt-1">
        <p className="line-clamp-2 text-[11.5px] leading-snug" style={{ color: "var(--ink-dim)" }}>
          {service.responsibility}
        </p>
      </div>

      <div className="flex items-center justify-between border-t px-3.5 py-2"
        style={{ borderColor: "var(--line-soft)" }}>
        <span className="font-mono text-[10px]" style={{ color: accent }}>
          {service.data_store}
        </span>
        <span className="font-mono text-[10px]" style={{ color: "var(--ink-faint)" }}>
          {service.key_apis.length} APIs
        </span>
      </div>

      <Handle type="source" position={Position.Bottom} style={{ background: "var(--line)", width: 7, height: 7, border: "none" }} />
    </div>
  );
}
