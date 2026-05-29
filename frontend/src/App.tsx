import { useCallback, useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Download, Activity } from "lucide-react";
import { analyzeStream } from "@/lib/api";
import type { Architecture, StepEvent } from "@/types/architecture";
import { PIPELINE_STEPS } from "@/types/architecture";
import Logo from "@/components/Logo";
import InputPanel from "@/components/InputPanel";
import PipelineConsole from "@/components/PipelineConsole";
import ServiceMap from "@/components/ServiceMap";
import ServiceDrawer from "@/components/ServiceDrawer";
import CompetitorPanel from "@/components/CompetitorPanel";
import ResultsSkeleton from "@/components/ResultsSkeleton";

type StepStatus = "pending" | "running" | "done";
type BackendState = "checking" | "online" | "offline";

function initialStatuses(): Record<string, StepStatus> {
  const o: Record<string, StepStatus> = {};
  PIPELINE_STEPS.forEach((s) => (o[s.key] = "pending"));
  return o;
}

export default function App() {
  const [running, setRunning] = useState(false);
  const [statuses, setStatuses] = useState(initialStatuses);
  const [arch, setArch] = useState<Architecture | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backend, setBackend] = useState<BackendState>("checking");

  // Ping the backend so the header shows a real status, not a fake tag.
  useEffect(() => {
    let alive = true;
    fetch("http://localhost:8000/api/health")
      .then((r) => (r.ok ? setBackend("online") : setBackend("offline")))
      .catch(() => alive && setBackend("offline"));
    return () => {
      alive = false;
    };
  }, []);

  const selectedService = useMemo(
    () => arch?.services.find((s) => s.id === selectedId) ?? null,
    [arch, selectedId]
  );

  const onSelect = useCallback((id: string) => setSelectedId(id || null), []);

  function exportJson() {
    if (!arch) return;
    const blob = new Blob([JSON.stringify(arch, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${arch.app_type.replace(/\s+/g, "-").toLowerCase()}-architecture.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function run(doc: string) {
    setRunning(true);
    setError(null);
    setArch(null);
    setSelectedId(null);
    setStatuses(initialStatuses());

    try {
      const result = await analyzeStream(doc, (e: StepEvent) => {
        if (e.step === "result") return;
        setStatuses((prev) => {
          const next = { ...prev };
          if (e.status === "running") next[e.step] = "running";
          if (e.status === "done") next[e.step] = "done";
          return next;
        });
      });
      setArch(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="min-h-screen">
      {/* Glass header */}
      <header className="glass sticky top-0 z-30 border-b" style={{ borderColor: "var(--line)" }}>
        <div className="mx-auto flex max-w-[1400px] items-center gap-3 px-6 py-3.5">
          <Logo size={38} />
          <div>
            <h1 className="font-mono text-lg font-extrabold tracking-tight" style={{ color: "var(--ink)" }}>
              Arch<span className="accent-amber">AI</span>tect
            </h1>
            <p className="text-[10px]" style={{ color: "var(--ink-faint)" }}>
              Requirements → microservice architecture
            </p>
          </div>

          <div className="ml-auto flex items-center gap-2.5">
            {/* real backend status */}
            <div className="flex items-center gap-2 rounded-lg px-3 py-1.5"
              style={{ border: "1px solid var(--line)", background: "rgba(255,255,255,0.015)" }}>
              <span
                className={backend === "online" ? "pulse" : ""}
                style={{
                  width: 7, height: 7, borderRadius: 99,
                  background: backend === "online" ? "var(--cyan)" : backend === "offline" ? "var(--rose)" : "var(--amber)",
                  boxShadow: backend === "online" ? "0 0 8px var(--cyan)" : "none",
                }}
              />
              <span className="font-mono text-[10px]" style={{ color: "var(--ink-dim)" }}>
                {backend === "online" ? "engine online" : backend === "offline" ? "engine offline" : "connecting…"}
              </span>
            </div>

            {/* export — only useful once we have a result */}
            <button
              onClick={exportJson}
              disabled={!arch}
              className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-mono text-[10px] transition-colors"
              style={{
                border: "1px solid var(--line)",
                color: arch ? "var(--cyan)" : "var(--ink-faint)",
                cursor: arch ? "pointer" : "not-allowed",
                background: "rgba(255,255,255,0.015)",
              }}
            >
              <Download size={12} />
              export json
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1400px] px-6 py-6">
        {/* Top row: input + pipeline */}
        <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1.6fr_1fr]">
          <InputPanel onRun={run} running={running} />
          <PipelineConsole statuses={statuses} active={running} />
        </div>

        {error && (
          <div className="panel mt-5 p-4" style={{ borderColor: "var(--rose)" }}>
            <span className="font-mono text-xs" style={{ color: "var(--rose)" }}>error: {error}</span>
          </div>
        )}

        {/* Skeleton while running */}
        {running && !arch && <ResultsSkeleton />}

        {/* Empty state */}
        {!arch && !running && !error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="panel mt-5 flex h-[420px] flex-col items-center justify-center"
          >
            <Activity size={28} style={{ color: "var(--ink-faint)" }} />
            <div className="mt-4 font-mono text-sm" style={{ color: "var(--ink-faint)" }}>
              <span className="cursor-blink">awaiting requirements</span>
            </div>
            <p className="mt-2 max-w-md text-center text-xs" style={{ color: "var(--ink-faint)" }}>
              Paste a spec or load the sample, then run the pipeline to see a decomposed
              service map, dependency graph, and live competitor intelligence.
            </p>
          </motion.div>
        )}

        {/* Results */}
        {arch && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="mt-5">
            {/* Summary strip */}
            <div className="panel panel-hover mb-5 flex flex-wrap items-center gap-x-6 gap-y-2 px-5 py-4">
              <div>
                <span className="font-mono text-[10px]" style={{ color: "var(--ink-faint)" }}>DOMAIN</span>
                <div className="text-sm font-semibold" style={{ color: "var(--ink)" }}>{arch.app_type}</div>
              </div>
              <div className="h-8 w-px" style={{ background: "var(--line)" }} />
              <div className="flex gap-5">
                <Stat n={arch.services.length} label="services" />
                <Stat n={arch.edges.length} label="dependencies" />
                <Stat n={arch.edges.filter((e) => e.type === "async").length} label="async flows" />
                <Stat n={arch.actors.length} label="actors" />
              </div>
              {arch.preprocess?.compressed && (
                <div className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5"
                  style={{ background: "rgba(56,225,212,0.06)", border: "1px solid var(--line)" }}>
                  <span style={{ width: 6, height: 6, borderRadius: 99, background: "var(--cyan)" }} />
                  <span className="font-mono text-[10px]" style={{ color: "var(--ink-dim)" }}>
                    doc compressed{" "}
                    <span className="accent-cyan">
                      {Math.round((1 - arch.preprocess.digest_chars / arch.preprocess.original_chars) * 100)}%
                    </span>{" "}
                    before LLM
                  </span>
                </div>
              )}
              <p className="ml-auto max-w-md text-xs" style={{ color: "var(--ink-dim)" }}>{arch.summary}</p>
            </div>

            {/* Map + competitor */}
            <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1.7fr_1fr]">
              <ServiceMap arch={arch} selectedId={selectedId} onSelect={onSelect} />
              <div className="max-h-[560px] overflow-y-auto">
                <CompetitorPanel data={arch.competitor} />
              </div>
            </div>

            {/* Shared concerns */}
            <div className="panel mt-5 px-5 py-4">
              <span className="font-mono text-[10px] tracking-wider" style={{ color: "var(--ink-faint)" }}>
                CROSS-CUTTING CONCERNS
              </span>
              <div className="mt-2 flex flex-wrap gap-2">
                {arch.shared_concerns.map((c) => (
                  <span key={c} className="tag">{c}</span>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </main>

      <ServiceDrawer arch={arch ?? ({} as Architecture)} service={selectedService} onClose={() => setSelectedId(null)} />
    </div>
  );
}

function Stat({ n, label }: { n: number; label: string }) {
  return (
    <div>
      <span className="font-mono text-lg font-bold accent-cyan">{n}</span>
      <span className="ml-1.5 text-[11px]" style={{ color: "var(--ink-faint)" }}>{label}</span>
    </div>
  );
}
