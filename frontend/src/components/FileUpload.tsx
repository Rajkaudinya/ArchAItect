import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, AlertTriangle } from 'lucide-react';

interface FileUploadProps {
  onUploadSuccess: (data: any) => void;
  projectId: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess, projectId }) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const processFile = async (file: File) => {
    const validExtensions = ['.txt', '.md', '.pdf', '.docx'];
    const fileExt = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!validExtensions.includes(fileExt)) {
      setError(`Unsupported file extension ${fileExt}. Please upload TXT, MD, PDF, or DOCX.`);
      return;
    }

    setIsLoading(true);
    setError(null);
    setUploadedFile(file.name);

    try {
      const formData = new FormData();
      formData.append("project_id", projectId);
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/api/v1/analysis/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errDetail = await response.json();
        throw new Error(errDetail.detail || "Server failed to parse document");
      }

      const result = await response.json();
      onUploadSuccess(result);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to analyze document. Make sure the backend service is running.");
      setUploadedFile(null);
    } finally {
      setIsLoading(false);
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  return (
    <div className="w-full">
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all duration-300 relative overflow-hidden ${
          isDragActive 
            ? "border-emerald-500 bg-emerald-500/5 shadow-[0_0_15px_rgba(16,185,129,0.1)]" 
            : "border-slate-800 bg-slate-900/35 hover:border-slate-700 hover:bg-slate-900/50"
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
          <div className="flex flex-col items-center justify-center py-6">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500 mb-4" />
            <h4 className="text-lg font-semibold text-white">AI Solution Architect Analyzing...</h4>
            <p className="text-sm text-gray-400 mt-1.5 max-w-md">
              Extracting domain models, mapping bounded contexts, and generating REST APIs.
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-4">
            <div className="p-4 bg-slate-800/80 rounded-2xl border border-slate-700/50 text-emerald-400 mb-4">
              <Upload size={28} className="animate-pulse" />
            </div>
            <h4 className="text-lg font-semibold text-white">Upload Requirement Documents</h4>
            <p className="text-sm text-gray-400 mt-1 max-w-sm">
              Drag & drop your SRS, BRD, User Story, or functional spec file here, or click to browse.
            </p>
            <div className="mt-4 flex flex-wrap gap-2 justify-center">
              {['TXT', 'Markdown', 'PDF', 'DOCX'].map((f) => (
                <span key={f} className="text-[10px] bg-slate-800 text-slate-400 border border-slate-700 px-2 py-0.5 rounded-md font-mono">
                  {f}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* File status updates */}
      {uploadedFile && !isLoading && (
        <div className="mt-3 flex items-center gap-2.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-4 py-2.5 rounded-xl text-xs font-medium">
          <CheckCircle size={15} />
          <span>Successfully analyzed <strong>{uploadedFile}</strong>! View the generated services below.</span>
        </div>
      )}

      {error && (
        <div className="mt-3 flex items-center gap-2.5 bg-rose-500/10 border border-rose-500/20 text-rose-400 px-4 py-2.5 rounded-xl text-xs font-medium">
          <AlertTriangle size={15} />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
