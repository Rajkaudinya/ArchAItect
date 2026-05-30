import React, { useState, useRef, useEffect } from 'react';
import { Upload, CheckCircle, AlertTriangle, FileText } from 'lucide-react';

interface FileUploadProps {
  onUploadSuccess: (data: any) => void;
  projectId: string;
}

const PARSE_STAGES = [
  { id: 'read',     label: 'Reading document',       duration: 600  },
  { id: 'nlp',      label: 'NLP tokenisation',        duration: 900  },
  { id: 'ddd',      label: 'DDD boundary detection',  duration: 1100 },
  { id: 'context',  label: 'Bounded context mapping', duration: 800  },
  { id: 'services', label: 'Service extraction',      duration: 1000 },
  { id: 'apis',     label: 'REST API generation',     duration: 700  },
  { id: 'metrics',  label: 'Architecture scoring',    duration: 600  },
  { id: 'trace',    label: 'Traceability matrix',     duration: 500  },
];

type StageStatus = 'pending' | 'active' | 'done';

function ParsingLoader({ filename }: { filename: string }) {
  const [stages, setStages] = useState(
    PARSE_STAGES.map(s => ({ ...s, status: 'pending' as StageStatus }))
  );
  const [barHeights, setBarHeights] = useState<number[]>(
    Array.from({ length: 20 }, () => Math.random() * 55 + 20)
  );

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    let elapsed = 0;

    PARSE_STAGES.forEach((stage, idx) => {
      const t1 = setTimeout(() => {
        setStages(prev => prev.map((s, i) => i === idx ? { ...s, status: 'active' } : s));
      }, elapsed);
      const t2 = setTimeout(() => {
        setStages(prev => prev.map((s, i) => i === idx ? { ...s, status: 'done' } : s));
      }, elapsed + stage.duration);
      timers.push(t1, t2);
      elapsed += stage.duration;
    });

    const barInterval = setInterval(() => {
      setBarHeights(Array.from({ length: 20 }, () => Math.random() * 65 + 15));
    }, 280);
    timers.push(barInterval as unknown as ReturnType<typeof setTimeout>);

    return () => timers.forEach(clearTimeout);
  }, []);

  const activeIdx  = stages.findIndex(s => s.status === 'active');
  const doneCount  = stages.filter(s => s.status === 'done').length;
  const progress   = Math.round((doneCount / stages.length) * 100);

  return (
    <div className="space-y-4 py-2">
      {/* File name badge */}
      <div className="flex items-center gap-2">
        <div className="w-7 h-7 rounded-lg bg-[var(--cyan-soft)] border border-[var(--border-cyan)] flex items-center justify-center flex-shrink-0">
          <FileText size={13} style={{ color: 'var(--cyan-deep)' }} />
        </div>
        <span className="font-mono-custom text-[10px] text-[var(--text-secondary)] truncate">{filename}</span>
        <span className="badge-cyan text-[8px] px-2 py-0.5 rounded-full ml-auto">Analysing</span>
      </div>

      {/* Bar graph */}
      <div className="flex items-end gap-[2px] h-10 px-1 rounded-xl overflow-hidden" style={{ background: 'rgba(240,244,248,0.8)' }}>
        {barHeights.map((h, i) => {
          const isFilled = i <= ((activeIdx / PARSE_STAGES.length) * barHeights.length);
          return (
            <div
              key={i}
              className="flex-1 rounded-t-sm transition-all duration-300"
              style={{
                height: `${h}%`,
                background: isFilled
                  ? `linear-gradient(180deg, var(--cyan) 0%, var(--cyan-deep) 100%)`
                  : 'rgba(0, 212, 232, 0.12)',
              }}
            />
          );
        })}
      </div>

      {/* Progress bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between items-center">
          <span className="font-mono-custom text-[9px] text-[var(--cyan-deep)] tracking-wider uppercase truncate max-w-[200px]">
            {stages[activeIdx]?.label ?? 'Finalising...'}
          </span>
          <span className="font-mono-custom text-[9px] text-[var(--text-muted)] font-bold">{progress}%</span>
        </div>
        <div className="h-1.5 rounded-full bg-[var(--border-light)] overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{
              width: `${progress}%`,
              background: 'linear-gradient(90deg, var(--cyan) 0%, var(--cyan-deep) 100%)',
            }}
          />
        </div>
      </div>

      {/* Stage pills grid */}
      <div className="grid grid-cols-2 gap-1.5">
        {stages.map(stage => (
          <div key={stage.id} className={`parse-stage ${stage.status}`}>
            <div className="parse-stage-dot" />
            <span className="text-[9px] truncate">{stage.label}</span>
            {stage.status === 'done' && (
              <CheckCircle size={9} style={{ color: 'var(--emerald)' }} className="ml-auto flex-shrink-0" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess, projectId }) => {
  const [isDragActive,  setIsDragActive]  = useState(false);
  const [isLoading,     setIsLoading]     = useState(false);
  const [error,         setError]         = useState<string | null>(null);
  const [uploadedFile,  setUploadedFile]  = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setIsDragActive(true);
    else if (e.type === 'dragleave') setIsDragActive(false);
  };

  const processFile = async (file: File) => {
    const validExt = ['.txt', '.md', '.pdf', '.docx'];
    const ext = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
    if (!validExt.includes(ext)) {
      setError(`Unsupported type ${ext}. Please upload TXT, MD, PDF, or DOCX.`);
      return;
    }

    setIsLoading(true);
    setError(null);
    setUploadedFile(file.name);

    try {
      const formData = new FormData();
      formData.append('project_id', projectId);
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/v1/analysis/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errDetail = await response.json();
        throw new Error(errDetail.detail || errDetail.error || 'Server failed to parse document');
      }

      onUploadSuccess(await response.json());
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Failed to analyze document. Make sure the backend is running.');
      setUploadedFile(null);
    } finally {
      setIsLoading(false);
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files?.[0]) processFile(e.dataTransfer.files[0]);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) processFile(e.target.files[0]);
  };

  return (
    <div className="w-full">
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => !isLoading && fileInputRef.current?.click()}
        className={`relative rounded-2xl border-2 border-dashed transition-all duration-300 overflow-hidden ${
          isLoading
            ? 'cursor-default border-[var(--cyan)] bg-[var(--cyan-soft)]'
            : isDragActive
            ? 'cursor-copy border-[var(--cyan)] bg-[var(--cyan-soft)] shadow-[0_0_28px_rgba(0,212,232,0.2)]'
            : 'cursor-pointer border-[var(--border-mid)] hover:border-[var(--cyan)] hover:bg-[var(--cyan-soft)] hover:shadow-[0_0_20px_rgba(0,212,232,0.12)]'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".txt,.md,.pdf,.docx"
          onChange={handleFileInput}
          disabled={isLoading}
        />

        {isLoading ? (
          <div className="p-5">
            <ParsingLoader filename={uploadedFile ?? 'document'} />
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-8 px-4 text-center">
            <div
              className={`mb-3 w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300 ${
                isDragActive
                  ? 'bg-[var(--cyan)] shadow-[0_0_20px_rgba(0,212,232,0.4)]'
                  : 'bg-[var(--cyan-soft)] border border-[var(--border-cyan)]'
              }`}
            >
              <Upload
                size={22}
                style={{ color: isDragActive ? 'white' : 'var(--cyan-deep)' }}
                className={isDragActive ? 'animate-bounce' : ''}
              />
            </div>
            <p className="font-display text-sm font-bold text-[var(--text-primary)] mb-1">
              {isDragActive ? 'Drop to analyse' : 'Upload Requirements'}
            </p>
            <p className="text-xs text-[var(--text-secondary)] mb-4 leading-relaxed">
              Drag & drop SRS, BRD, or functional spec files, or click to browse.
            </p>
            <div className="flex flex-wrap gap-1.5 justify-center">
              {['TXT', 'Markdown', 'PDF', 'DOCX'].map(f => (
                <span key={f} className="badge-cyan font-mono-custom text-[9px] px-2 py-0.5 rounded-lg">
                  {f}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {uploadedFile && !isLoading && (
        <div className="mt-2.5 flex items-center gap-2 badge-emerald px-3.5 py-2.5 rounded-xl text-xs font-medium">
          <CheckCircle size={13} />
          <span>Analysed <strong>{uploadedFile}</strong> — view services below.</span>
        </div>
      )}

      {error && (
        <div className="mt-2.5 flex items-center gap-2 badge-coral px-3.5 py-2.5 rounded-xl text-xs font-medium">
          <AlertTriangle size={13} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};