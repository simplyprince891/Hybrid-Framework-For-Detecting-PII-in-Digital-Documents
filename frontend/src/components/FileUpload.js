import React, { useState, useEffect, useRef } from "react";
import { toast } from 'react-toastify';

function FileUpload({ onUpload }) {
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [documentId, setDocumentId] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleChange = e => setFile(e.target.files[0]);

  const handleDrop = e => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer?.files?.[0];
    if (f) setFile(f);
  };

  const handleSubmit = async e => {
    e && e.preventDefault();
    if (!file) return toast.warn('Please choose a file first');
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("/api/v1/upload_async/", { method: "POST", body: formData });
      const data = await res.json();
      if (data.job_id) {
        setJobId(data.job_id);
        setStatus("pending");
        toast.info('Upload queued — processing...');
      } else {
        toast.error('Upload failed');
      }
    } catch (err) {
      console.error(err);
      toast.error('Upload error');
    }
  };

  // poll job status when jobId is set
  useEffect(() => {
    if (!jobId) return;
    let mounted = true;
    const poll = async () => {
      try {
        const res = await fetch(`/api/v1/upload_status/${jobId}`);
        const data = await res.json();
        if (!mounted) return;
        setStatus(data.status || null);
        if (data.status === "done") {
          setDocumentId(data.result?.document_id || null);
          if (data.result?.document_id) {
            const r2 = await fetch(`/api/v1/report/?document_id=${data.result.document_id}`);
            if (r2.ok) {
              const rep = await r2.json();
              onUpload(rep.detections || []);
              toast.success('Processing complete');
            }
          }
        }
        if (data.status && data.status !== "done" && data.status !== "error") {
          setTimeout(poll, 900);
        }
      } catch (err) {
        console.error(err);
        // keep polling but slower
        setTimeout(poll, 1500);
      }
    };
    poll();
    return () => { mounted = false; };
  }, [jobId, onUpload]);

  const handleDownloadRedacted = async () => {
    if (!documentId) return;
    const url = `/api/v1/export/redacted_pdf/?document_id=${documentId}`;
    try {
      const res = await fetch(url);
      if (!res.ok) {
        const txt = await res.text();
        toast.error(`Failed to get redacted PDF: ${res.status}`);
        return;
      }
      const blob = await res.blob();
      const link = document.createElement('a');
      const href = URL.createObjectURL(blob);
      link.href = href;
      link.download = `redacted_${documentId}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(href);
      toast.success('Redacted PDF download started');
    } catch (err) {
      console.error(err);
      toast.error('Failed to download redacted PDF');
    }
  };

  return (
    <div className="bg-white p-4 rounded shadow-sm">
      <form onSubmit={handleSubmit} className="space-y-3">
        <div
          className={`border-2 border-dashed rounded p-6 text-center cursor-pointer transition ${dragOver ? 'bg-gray-50 border-blue-400' : 'border-gray-200'}`}
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={e => { e.preventDefault(); setDragOver(false); }}
          onDrop={handleDrop}
          onClick={() => inputRef.current && inputRef.current.click()}
        >
          <input ref={inputRef} type="file" onChange={handleChange} className="hidden" />
          <div className="flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16V8a4 4 0 014-4h2a4 4 0 014 4v8" /></svg>
            <div>
              <div className="text-sm font-medium text-gray-700">Drag & drop a file here, or click to select</div>
              <div className="text-xs text-gray-500">PDF, TXT, or images — max size allowed by server</div>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex-1 text-sm text-gray-700">{file ? file.name : <span className="text-gray-400">No file selected</span>}</div>
          <button
            type="submit"
            className={`px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60`}
            disabled={!file || !!jobId}
          >
            {jobId ? 'Processing...' : 'Upload'}
          </button>
          <button
            type="button"
            onClick={() => { setFile(null); setJobId(null); setStatus(null); setDocumentId(null); }}
            className="px-3 py-2 rounded bg-gray-100 text-sm text-gray-700 hover:bg-gray-200"
          >
            Reset
          </button>
        </div>
      </form>

      {jobId && (
        <div className="mt-4 text-sm text-gray-700">
          <div className="flex items-center space-x-2">
            <strong>Job:</strong>
            <span className="font-mono text-xs px-2 py-1 bg-gray-100 rounded">{jobId}</span>
            <span className="ml-2">Status:</span>
            <span className={`ml-1 font-semibold ${status === 'done' ? 'text-green-600' : status === 'error' ? 'text-red-600' : 'text-yellow-600'}`}>{status}</span>
            {status === 'pending' && (
              <svg className="w-4 h-4 animate-spin text-gray-600 ml-2" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path></svg>
            )}
          </div>

          {status === 'done' && documentId && (
            <div className="mt-3">
              <button onClick={handleDownloadRedacted} className="px-3 py-2 rounded bg-green-600 text-white hover:bg-green-700">Download redacted PDF</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default FileUpload;
