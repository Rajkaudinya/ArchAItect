import { motion } from "framer-motion";
import { PIPELINE_STEPS } from "@/types/architecture";

type StepStatus = "pending" | "running" | "done";

interface Props {
  statuses: Record<string, StepStatus>;
  active: boolean;
}

function Dot({ status }: { status: StepStatus }) {
  if (status === "done") {
    return (
      <span className="flex h-5 w-5 items-center justify-center rounded-full"
        style={{ background: "rgba(56,225,212,0.12)", border: "1px solid var(--cyan)" }}>
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none"
          stroke="var(--cyan)" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="20 6 9 17 4 12" />
        </svg>
      </span>
    );
  }
  if (status === "running") {
    return (
      <span className="relative flex h-5 w-5 items-center justify-center">
        <span className="absolute h-5 w-5 rounded-full"
          style={{ border: "1px solid var(--amber)", borderTopColor: "transparent", animation: "spin 0.8s linear infinite" }} />
        <span className="h-1.5 w-1.5 rounded-full" style={{ background: "var(--amber)" }} />
      </span>
    );
  }
  return (
    <span className="flex h-5 w-5 items-center justify-center rounded-full"
      style={{ border: "1px solid var(--line)" }}>
      <span className="h-1.5 w-1.5 rounded-full" style={{ background: "var(--ink-faint)" }} />
    </span>
  );
}

export default function PipelineConsole({ statuses, active }: Props) {
  return (
    <div className="panel panel-glow p-5">
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      <div className="mb-4 flex items-center gap-2">
        <span className="h-2 w-2 rounded-full" style={{ background: active ? "var(--amber)" : "var(--ink-faint)" }} />
        <span className="font-mono text-xs tracking-wider" style={{ color: "var(--ink-dim)" }}>
          AGENT PIPELINE
        </span>
        <span className="ml-auto font-mono text-[10px]" style={{ color: "var(--ink-faint)" }}>
          5 agents · sequential
        </span>
      </div>

      <div className="space-y-1">
        {PIPELINE_STEPS.map((step, i) => {
          const s = statuses[step.key] ?? "pending";
          return (
            <motion.div
              key={step.key}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
              className="relative flex items-center gap-3 overflow-hidden rounded-lg px-3 py-2.5"
              style={{
                background: s === "running" ? "rgba(255,179,71,0.04)" : "transparent",
                border: `1px solid ${s === "running" ? "rgba(255,179,71,0.18)" : "transparent"}`,
              }}
            >
              {s === "running" && <span className="shimmer absolute inset-0 rounded-lg" />}
              <span className="font-mono text-[10px] w-5" style={{ color: "var(--ink-faint)" }}>
                {String(i + 1).padStart(2, "0")}
              </span>
              <Dot status={s} />
              <span
                className="text-sm"
                style={{
                  color: s === "pending" ? "var(--ink-faint)" : "var(--ink)",
                  fontWeight: s === "running" ? 600 : 400,
                }}
              >
                {step.label}
              </span>
              {s === "running" && (
                <span className="ml-auto font-mono text-[10px] accent-amber cursor-blink">working</span>
              )}
              {s === "done" && (
                <span className="ml-auto font-mono text-[10px] accent-cyan">ok</span>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
