import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';
import type {
  TinyFishStatus,
  DataSource,
  ExtractionJob,
  SourceRecord,
} from '../types';
import {
  Bot,
  Play,
  CheckCircle2,
  Clock,
  ShieldCheck,
  RefreshCw,
  FileCode2,
  ExternalLink,
  X,
  Copy,
  Check
} from 'lucide-react';

export const TinyFishIntelligencePage: React.FC = () => {
  const { t } = useLanguage();

  const [statusInfo, setStatusInfo] = useState<TinyFishStatus | null>(null);
  const [sources, setSources] = useState<DataSource[]>([]);
  const [jobs, setJobs] = useState<ExtractionJob[]>([]);
  const [loading, setLoading] = useState(true);

  // Trigger Extraction Modal
  const [showTriggerModal, setShowTriggerModal] = useState(false);
  const [targetUrl, setTargetUrl] = useState('https://nfsa.gov.in/public/nfsadashboard/PublicAllocationDashboard.aspx');
  const [executionMode, setExecutionMode] = useState<'AUTO' | 'LIVE' | 'DEMO'>('AUTO');
  const [reportingPeriod, setReportingPeriod] = useState('2026-09');
  const [triggering, setTriggering] = useState(false);
  const [triggerResult, setTriggerResult] = useState<ExtractionJob | null>(null);

  // Selected Job for Records & JSON inspection
  const [selectedJob, setSelectedJob] = useState<ExtractionJob | null>(null);
  const [jobRecords, setJobRecords] = useState<SourceRecord[]>([]);
  const [loadingRecords, setLoadingRecords] = useState(false);
  const [copiedJson, setCopiedJson] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sRes, srcRes, jRes] = await Promise.all([
        api.tinyfish.getStatus(),
        api.tinyfish.getSources(),
        api.tinyfish.getJobs(20),
      ]);
      setStatusInfo(sRes);
      setSources(srcRes);
      setJobs(jRes);
    } catch (err) {
      console.error("Failed to load TinyFish data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleTrigger = async (e: React.FormEvent) => {
    e.preventDefault();
    setTriggering(true);
    setTriggerResult(null);

    try {
      const res = await api.tinyfish.triggerJob({
        url: targetUrl,
        reporting_period: reportingPeriod,
        mode: executionMode,
      });
      setTriggerResult(res);
      await loadData();
    } catch (err: any) {
      alert(`Extraction Trigger Error: ${err.message}`);
    } finally {
      setTriggering(false);
    }
  };

  const handleInspectJob = async (job: ExtractionJob) => {
    setSelectedJob(job);
    setLoadingRecords(true);
    try {
      const recs = await api.tinyfish.getJobRecords(job.id);
      setJobRecords(recs);
    } catch (err) {
      console.error("Failed to load records for job:", err);
    } finally {
      setLoadingRecords(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#fcfaf7] flex items-center justify-center py-12">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-[#1b5e3a] border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-xs font-semibold text-gray-600">Loading TinyFish Agent Center...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#fcfaf7] py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header Banner */}
        <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-emerald-700 flex items-center justify-center text-white shadow-xs">
              <Bot className="w-8 h-8 text-amber-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
                  {t('tinyfish_title')}
                </h1>
                <span className="text-xs bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
                  OFFICIAL API v1
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1 max-w-xl">
                {t('tinyfish_desc')}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <button
              onClick={() => {
                setShowTriggerModal(true);
                setTriggerResult(null);
              }}
              className="w-full md:w-auto flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[#1b5e3a] hover:bg-[#164e2e] text-white text-xs font-bold shadow-xs transition-all cursor-pointer"
            >
              <Play className="w-4 h-4 fill-white" />
              <span>{t('trigger_extraction')}</span>
            </button>
          </div>
        </div>

        {/* Integration Engine Status Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">API Key Configured</div>
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${statusInfo?.configured ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
              <span className="text-lg font-bold text-gray-900">
                {statusInfo?.configured ? 'LIVE KEY DETECTED' : 'DEMO MODE'}
              </span>
            </div>
            <div className="text-[11px] text-gray-500 mt-1">
              {statusInfo?.configured ? 'Authenticated via X-API-Key' : 'Using labelled DEMO fixtures'}
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">Documented Base URL</div>
            <div className="text-sm font-mono font-bold text-[#1b5e3a] truncate">
              {statusInfo?.base_url ?? 'https://agent.tinyfish.ai'}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">POST /v1/automation/run</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">Approved Sources</div>
            <div className="text-2xl font-bold text-gray-900">
              {statusInfo?.approved_sources_count ?? sources.length}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Protected by Admin Allowlist</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">Extraction Jobs</div>
            <div className="text-2xl font-bold text-gray-900">
              {statusInfo?.total_jobs_count ?? jobs.length}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Persisted in database</div>
          </div>
        </div>

        {/* Section 1: Admin-Approved Source Allowlist */}
        <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-[#1b5e3a]" />
                {t('approved_sources')}
              </h2>
              <p className="text-xs text-gray-500">
                To prevent SSRF and unsafe crawling, TinyFish only visits administrator-approved public portals.
              </p>
            </div>
            <span className="text-[11px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 px-2.5 py-1 rounded">
              Allowlist Active
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#fcfaf7] border-y border-[#e5dfd5] text-gray-600 font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Portal Name</th>
                  <th className="py-2.5 px-3">Target URL</th>
                  <th className="py-2.5 px-3">Jurisdiction</th>
                  <th className="py-2.5 px-3">Source Type</th>
                  <th className="py-2.5 px-3">Approval Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {sources.map((src) => (
                  <tr key={src.id} className="hover:bg-gray-50/60">
                    <td className="py-2.5 px-3 font-semibold text-gray-900">{src.name}</td>
                    <td className="py-2.5 px-3 font-mono text-gray-600">
                      <a
                        href={src.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="hover:underline flex items-center gap-1 text-[#1b5e3a]"
                      >
                        <span className="truncate max-w-sm">{src.source_url}</span>
                        <ExternalLink className="w-3 h-3 shrink-0" />
                      </a>
                    </td>
                    <td className="py-2.5 px-3 text-gray-600">{src.jurisdiction}</td>
                    <td className="py-2.5 px-3">
                      <span className="bg-gray-100 px-2 py-0.5 rounded font-mono text-[10px]">
                        {src.source_type}
                      </span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className="inline-flex items-center gap-1 text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded text-[11px]">
                        <CheckCircle2 className="w-3 h-3" />
                        Approved
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Section 2: Extraction Jobs & History */}
        <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <Clock className="w-5 h-5 text-[#d97706]" />
                {t('extraction_history')}
              </h2>
              <p className="text-xs text-gray-500">
                Click any job to inspect the parsed food security records and SHA256 integrity hashes
              </p>
            </div>
            <button
              onClick={loadData}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors cursor-pointer"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Refresh</span>
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#fcfaf7] border-y border-[#e5dfd5] text-gray-600 font-semibold">
                <tr>
                  <th className="py-2.5 px-3">{t('job_id')}</th>
                  <th className="py-2.5 px-3">Source Portal</th>
                  <th className="py-2.5 px-3">Mode</th>
                  <th className="py-2.5 px-3">{t('records_count')}</th>
                  <th className="py-2.5 px-3">{t('status')}</th>
                  <th className="py-2.5 px-3">Execution Time</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {jobs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-6 text-center text-gray-400">
                      No extraction jobs recorded yet.
                    </td>
                  </tr>
                ) : (
                  jobs.map((job) => (
                    <tr key={job.id} className="hover:bg-gray-50/60">
                      <td className="py-2.5 px-3 font-mono font-bold text-gray-900">
                        #{job.id}
                      </td>
                      <td className="py-2.5 px-3">
                        <span className="font-semibold text-gray-900 block">{job.source_name}</span>
                        <span className="text-[10px] text-gray-400 truncate max-w-xs block">{job.source_url}</span>
                      </td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            job.mode === 'LIVE'
                              ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                              : 'bg-amber-100 text-amber-800 border border-amber-300'
                          }`}
                        >
                          {job.mode}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-bold text-gray-800">
                        {job.records_extracted} records
                      </td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            job.job_status === 'COMPLETED'
                              ? 'bg-emerald-100 text-emerald-800'
                              : job.job_status === 'FAILED'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-amber-100 text-amber-800 animate-pulse'
                          }`}
                        >
                          {job.job_status}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-gray-600">
                        {new Date(job.started_at).toLocaleString()}
                      </td>
                      <td className="py-2.5 px-3 text-right">
                        <button
                          onClick={() => handleInspectJob(job)}
                          className="inline-flex items-center gap-1 px-3 py-1 bg-white border border-gray-300 text-gray-800 font-medium rounded hover:bg-gray-50 shadow-2xs cursor-pointer"
                        >
                          <FileCode2 className="w-3.5 h-3.5 text-[#1b5e3a]" />
                          <span>Inspect</span>
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Trigger Extraction Modal */}
      {showTriggerModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-gray-200 space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Play className="w-5 h-5 text-[#1b5e3a]" />
                {t('trigger_extraction')}
              </h3>
              <button
                onClick={() => setShowTriggerModal(false)}
                className="text-gray-400 hover:text-gray-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {triggerResult ? (
              <div className="p-6 text-center space-y-4">
                <div className="w-12 h-12 bg-emerald-100 text-emerald-800 rounded-full flex items-center justify-center mx-auto">
                  <Check className="w-6 h-6" />
                </div>
                <h4 className="text-base font-bold text-gray-900">
                  Extraction Job Initiated
                </h4>
                <div className="text-xs text-gray-600 space-y-1">
                  <p>Job ID: <strong>#{triggerResult.id}</strong></p>
                  <p>Mode: <strong className="text-emerald-700">{triggerResult.mode}</strong></p>
                  <p>Records Extracted: <strong>{triggerResult.records_extracted}</strong></p>
                </div>
                <button
                  onClick={() => setShowTriggerModal(false)}
                  className="px-5 py-2 bg-[#1b5e3a] text-white text-xs font-semibold rounded-lg hover:bg-[#164e2e]"
                >
                  Done
                </button>
              </div>
            ) : (
              <form onSubmit={handleTrigger} className="space-y-4 text-xs">
                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    Select Target Public Portal (Admin-Approved):
                  </label>
                  <select
                    value={targetUrl}
                    onChange={(e) => setTargetUrl(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg bg-white font-medium"
                  >
                    {sources.map((s) => (
                      <option key={s.id} value={s.source_url}>
                        {s.name} ({s.jurisdiction})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    Reporting Period:
                  </label>
                  <input
                    type="text"
                    value={reportingPeriod}
                    onChange={(e) => setReportingPeriod(e.target.value)}
                    placeholder="2026-09"
                    className="w-full p-2 border border-gray-300 rounded-lg"
                    required
                  />
                </div>

                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    Execution Mode:
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      type="button"
                      onClick={() => setExecutionMode('AUTO')}
                      className={`p-2 rounded-lg border text-center font-bold transition-colors cursor-pointer ${
                        executionMode === 'AUTO'
                          ? 'border-[#1b5e3a] bg-[#1b5e3a]/10 text-[#1b5e3a]'
                          : 'border-gray-200 text-gray-600'
                      }`}
                    >
                      AUTO
                    </button>
                    <button
                      type="button"
                      onClick={() => setExecutionMode('LIVE')}
                      className={`p-2 rounded-lg border text-center font-bold transition-colors cursor-pointer ${
                        executionMode === 'LIVE'
                          ? 'border-emerald-600 bg-emerald-50 text-emerald-800'
                          : 'border-gray-200 text-gray-600'
                      }`}
                    >
                      LIVE API
                    </button>
                    <button
                      type="button"
                      onClick={() => setExecutionMode('DEMO')}
                      className={`p-2 rounded-lg border text-center font-bold transition-colors cursor-pointer ${
                        executionMode === 'DEMO'
                          ? 'border-amber-600 bg-amber-50 text-amber-800'
                          : 'border-gray-200 text-gray-600'
                      }`}
                    >
                      DEMO FIXTURE
                    </button>
                  </div>
                </div>

                <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-amber-800 text-[11px] leading-relaxed">
                  <strong>Non-Fabrication Policy:</strong> If LIVE mode is chosen and the API key is invalid or
                  unreachable, RationTrace never invents fake data; it logs an explicit failure.
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowTriggerModal(false)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={triggering}
                    className="px-4 py-2 bg-[#1b5e3a] text-white rounded-lg font-semibold hover:bg-[#164e2e] disabled:opacity-50"
                  >
                    {triggering ? 'Executing Web Agent...' : 'Launch Agent Extraction'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Inspect Job Records & Raw Output Modal */}
      {selectedJob && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-3xl w-full p-6 shadow-xl border border-gray-200 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b pb-3">
              <div>
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <FileCode2 className="w-5 h-5 text-[#1b5e3a]" />
                  Job #{selectedJob.id}: {selectedJob.source_name}
                </h3>
                <span className="text-xs text-gray-500 font-mono">
                  Mode: {selectedJob.mode} • Status: {selectedJob.job_status} • Extracted: {selectedJob.records_extracted} records
                </span>
              </div>
              <button
                onClick={() => setSelectedJob(null)}
                className="text-gray-400 hover:text-gray-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Parsed Source Records with SHA256 hashes */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                Parsed Normalized Records & Cryptographic Hashes
              </h4>

              {loadingRecords ? (
                <div className="p-8 text-center text-xs text-gray-500">Loading records...</div>
              ) : jobRecords.length === 0 ? (
                <div className="p-6 text-center text-xs text-gray-400 bg-gray-50 rounded-lg">
                  No source records stored for this run.
                </div>
              ) : (
                <div className="overflow-x-auto border border-gray-200 rounded-lg">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-[#fcfaf7] border-b text-gray-600 font-semibold">
                      <tr>
                        <th className="py-2 px-3">State</th>
                        <th className="py-2 px-3">Commodity</th>
                        <th className="py-2 px-3">Quantity</th>
                        <th className="py-2 px-3">Period</th>
                        <th className="py-2 px-3">SHA256 Hash</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {jobRecords.map((r) => (
                        <tr key={r.id} className="hover:bg-gray-50/60">
                          <td className="py-2 px-3 font-semibold text-gray-900">{r.region}</td>
                          <td className="py-2 px-3">{r.commodity}</td>
                          <td className="py-2 px-3 font-mono font-bold text-gray-800">{r.quantity} {r.unit}</td>
                          <td className="py-2 px-3 text-gray-600">{r.reporting_period}</td>
                          <td className="py-2 px-3 font-mono text-[10px] text-gray-500 truncate max-w-[140px]" title={r.record_hash}>
                            {r.record_hash.slice(0, 16)}...
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Structured JSON Preview */}
            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Structured JSON Result Payload
                </h4>
                <button
                  type="button"
                  onClick={() => copyToClipboard(JSON.stringify(jobRecords, null, 2))}
                  className="inline-flex items-center gap-1 text-[11px] font-semibold text-[#1b5e3a] hover:underline cursor-pointer"
                >
                  {copiedJson ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span>Copy JSON</span>
                    </>
                  )}
                </button>
              </div>
              <pre className="p-3 bg-gray-900 text-emerald-400 font-mono text-[11px] rounded-lg max-h-40 overflow-y-auto">
                {JSON.stringify(jobRecords, null, 2)}
              </pre>
            </div>

            {/* Close Button */}
            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedJob(null)}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-semibold text-xs cursor-pointer"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
