import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';
import type { Discrepancy, AuditSummary } from '../types';
import {
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  Search,
  Eye,
  X,
  RefreshCw,
} from 'lucide-react';

export const OfficialAuditPage: React.FC = () => {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [summary, setSummary] = useState<AuditSummary | null>(null);
  const [discrepancies, setDiscrepancies] = useState<Discrepancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [runningAudit, setRunningAudit] = useState(false);
  const [auditBanner, setAuditBanner] = useState<string | null>(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Selected Discrepancy for Evidence Inspection & Resolution Modal
  const [selectedDiscrepancy, setSelectedDiscrepancy] = useState<Discrepancy | null>(null);
  const [resolutionOutcome, setResolutionOutcome] = useState('DOCUMENTED_ADJUSTMENT_VERIFIED');
  const [investigationNote, setInvestigationNote] = useState('');
  const [resolving, setResolving] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, discRes] = await Promise.all([
        api.audits.getSummary(),
        api.audits.getDiscrepancies(),
      ]);
      setSummary(sumRes);
      setDiscrepancies(discRes);
    } catch (err) {
      console.error("Failed to load audit data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAuditEngine = async () => {
    setRunningAudit(true);
    setAuditBanner(null);
    try {
      const res = await api.audits.triggerAuditRun();
      setAuditBanner(res.message);
      await loadData();
    } catch (err: any) {
      alert(`Audit run failed: ${err.message}`);
    } finally {
      setRunningAudit(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDiscrepancy) return;

    setResolving(true);
    try {
      await api.audits.resolveDiscrepancy(selectedDiscrepancy.id, {
        outcome: resolutionOutcome,
        note: investigationNote || 'Inspector reconciled discrepancy against physical register vouchers.',
      });
      setSelectedDiscrepancy(null);
      setInvestigationNote('');
      await loadData();
    } catch (err: any) {
      alert(`Resolution failed: ${err.message}`);
    } finally {
      setResolving(false);
    }
  };

  const filteredDiscrepancies = discrepancies.filter((d) => {
    const matchesStatus = statusFilter === 'ALL' || d.status === statusFilter;
    const matchesSeverity = severityFilter === 'ALL' || d.severity === severityFilter;
    const matchesSearch =
      d.shop_identifier.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.shop_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.commodity.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.rule_triggered.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSeverity && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-[#fcfaf7] py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Title Bar */}
        <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#d97706] flex items-center justify-center text-white shadow-xs">
              <ShieldCheck className="w-8 h-8 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
                  {t('audit_dashboard_title')}
                </h1>
                <span className="text-xs bg-amber-100 text-amber-900 font-bold px-2 py-0.5 rounded-full">
                  OFFICIAL QUEUE
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Auditor: <strong>{user?.full_name ?? 'Ananya Verma (Inspector)'}</strong> • Department of Food & Public Distribution
              </p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <div className="text-xs bg-[#fcfaf7] p-3 rounded-xl border border-gray-200 text-gray-600 max-w-sm">
              <strong>Audit Standard:</strong> Balanced reconciliation requires 
              <code className="text-xs font-mono text-[#1b5e3a] ml-1 font-bold">Opening + Received - Distributed = Closing</code>.
            </div>
            <button
              onClick={handleRunAuditEngine}
              disabled={runningAudit}
              className="inline-flex items-center gap-2 bg-[#1b5e3a] hover:bg-[#154a2e] text-white px-4 py-2.5 rounded-xl font-medium text-xs shadow-sm transition disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${runningAudit ? 'animate-spin' : ''}`} />
              {runningAudit ? 'Running Audit Engine...' : '⚡ Run Full Audit Engine'}
            </button>
          </div>
        </div>

        {/* Audit Notification Banner */}
        {auditBanner && (
          <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 p-3.5 rounded-xl text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span>{auditBanner}</span>
            </div>
            <button onClick={() => setAuditBanner(null)} className="text-emerald-700 hover:text-emerald-900 text-xs font-bold">
              Dismiss
            </button>
          </div>
        )}

        {/* Audit Metrics Counters */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">{t('total_records')}</div>
            <div className="text-2xl font-bold text-gray-900">
              {loading ? '...' : summary?.total_records ?? '0'}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Validated electronic registers</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">{t('open_discrepancies')}</div>
            <div className="text-2xl font-bold text-amber-600">
              {loading ? '...' : summary?.open_discrepancies ?? '0'}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Require physical verification</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">{t('critical_alerts')}</div>
            <div className="text-2xl font-bold text-red-600">
              {loading ? '...' : summary?.critical_discrepancies ?? '0'}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Variance &gt; 1,000 kg threshold</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">{t('case_resolved')}</div>
            <div className="text-2xl font-bold text-emerald-700">
              {loading ? '...' : summary?.resolved_cases ?? '0'}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Closed with documented proof</div>
          </div>
        </div>

        {/* Rule Triggers Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/40 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-bold text-amber-900 uppercase">
                {t('rule_a_title')}
              </span>
              <p className="text-xs text-amber-800/80">
                Opening + Received - Distributed ≠ Recorded Closing Stock
              </p>
            </div>
            <span className="text-xl font-bold text-amber-900 bg-white px-3 py-1 rounded-lg border border-amber-200">
              {summary?.rule_a_count ?? 1}
            </span>
          </div>

          <div className="p-4 rounded-xl border border-red-200 bg-red-50/40 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-xs font-bold text-red-900 uppercase">
                {t('rule_b_title')}
              </span>
              <p className="text-xs text-red-800/80">
                Calculated or reported inventory becomes negative
              </p>
            </div>
            <span className="text-xl font-bold text-red-900 bg-white px-3 py-1 rounded-lg border border-red-200">
              {summary?.rule_b_count ?? 1}
            </span>
          </div>
        </div>

        {/* Discrepancy Table */}
        <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-[#d97706]" />
                Audited Discrepancy Case Queue
              </h2>
              <p className="text-xs text-gray-500">
                Filter by status, severity, or shop name to review calculation evidence
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search shop or rule..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="text-xs pl-8 pr-3 py-1.5 rounded-lg border border-gray-300 bg-white"
                />
              </div>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="text-xs py-1.5 px-2.5 rounded-lg border border-gray-300 bg-white font-medium"
              >
                <option value="ALL">All Statuses</option>
                <option value="OPEN">Open</option>
                <option value="UNDER_REVIEW">Under Review</option>
                <option value="RESOLVED">Resolved</option>
              </select>

              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="text-xs py-1.5 px-2.5 rounded-lg border border-gray-300 bg-white font-medium"
              >
                <option value="ALL">{t('all_severities')}</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#fcfaf7] border-y border-[#e5dfd5] text-gray-600 font-semibold">
                <tr>
                  <th className="py-2.5 px-3">{t('shop_col')}</th>
                  <th className="py-2.5 px-3">State / District</th>
                  <th className="py-2.5 px-3">{t('commodity')}</th>
                  <th className="py-2.5 px-3">Period</th>
                  <th className="py-2.5 px-3">{t('difference_col')}</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">{t('status')}</th>
                  <th className="py-2.5 px-3 text-right">{t('actions_col')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredDiscrepancies.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="py-8 text-center text-gray-400">
                      No audit cases match the selected filters.
                    </td>
                  </tr>
                ) : (
                  filteredDiscrepancies.map((d) => (
                    <tr key={d.id} className="hover:bg-gray-50/60 transition-colors">
                      <td className="py-3 px-3">
                        <span className="font-mono font-bold text-gray-900 block">{d.shop_identifier}</span>
                        <span className="text-[11px] text-gray-500">{d.shop_name}</span>
                      </td>
                      <td className="py-3 px-3 text-gray-600">
                        {d.state} ({d.district})
                      </td>
                      <td className="py-3 px-3 font-semibold text-gray-900">{d.commodity}</td>
                      <td className="py-3 px-3 text-gray-600">{d.reporting_period}</td>
                      <td className="py-3 px-3">
                        <span
                          className={`font-bold font-mono ${
                            d.difference < 0 ? 'text-red-700' : 'text-amber-700'
                          }`}
                        >
                          {d.difference > 0 ? `+${d.difference}` : d.difference} {d.unit}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            d.severity === 'CRITICAL'
                              ? 'bg-red-100 text-red-800'
                              : d.severity === 'HIGH'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}
                        >
                          {d.severity}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                            d.status === 'RESOLVED'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {d.status}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={() => setSelectedDiscrepancy(d)}
                          className="inline-flex items-center gap-1 px-3 py-1 bg-white border border-gray-300 text-gray-800 font-medium rounded-md hover:bg-gray-50 shadow-2xs transition-colors cursor-pointer"
                        >
                          <Eye className="w-3.5 h-3.5 text-[#1b5e3a]" />
                          <span>{t('inspect_case')}</span>
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

      {/* Case Evidence & Resolution Modal */}
      {selectedDiscrepancy && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-xl border border-gray-200 space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b pb-3">
              <div>
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-[#d97706]" />
                  Audit Case #{selectedDiscrepancy.id}: {selectedDiscrepancy.shop_identifier}
                </h3>
                <span className="text-xs text-gray-500">
                  {selectedDiscrepancy.shop_name} • {selectedDiscrepancy.state} ({selectedDiscrepancy.district})
                </span>
              </div>
              <button
                onClick={() => setSelectedDiscrepancy(null)}
                className="text-gray-400 hover:text-gray-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Evidence & Calculation Box */}
            <div className="p-4 bg-[#fcfaf7] rounded-xl border border-[#e5dfd5] space-y-3 text-xs">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <div>
                  <span className="text-gray-500 block text-[11px]">Commodity</span>
                  <strong className="text-gray-900 text-sm">{selectedDiscrepancy.commodity}</strong>
                </div>
                <div>
                  <span className="text-gray-500 block text-[11px]">Reporting Period</span>
                  <strong className="text-gray-900 text-sm">{selectedDiscrepancy.reporting_period}</strong>
                </div>
                <div>
                  <span className="text-gray-500 block text-[11px]">Expected Value</span>
                  <strong className="text-gray-900 text-sm">{selectedDiscrepancy.expected_value} {selectedDiscrepancy.unit}</strong>
                </div>
                <div>
                  <span className="text-gray-500 block text-[11px]">Observed Value</span>
                  <strong className="text-gray-900 text-sm">{selectedDiscrepancy.observed_value} {selectedDiscrepancy.unit}</strong>
                </div>
              </div>

              <div className="pt-2 border-t border-gray-200">
                <span className="text-gray-500 font-semibold block mb-1">
                  Triggered Rule & Mathematical Calculation:
                </span>
                <div className="font-mono bg-white p-2.5 rounded-lg border border-gray-200 text-gray-800 text-[11px]">
                  {selectedDiscrepancy.calculation_details || selectedDiscrepancy.reason}
                </div>
              </div>

              {selectedDiscrepancy.evidence_summary && (
                <div>
                  <span className="text-gray-500 font-semibold block mb-1">Evidence Summary:</span>
                  <p className="text-gray-700 bg-white p-2.5 rounded-lg border border-gray-200 text-[11px]">
                    {selectedDiscrepancy.evidence_summary}
                  </p>
                </div>
              )}
            </div>

            {/* Resolution Form */}
            {selectedDiscrepancy.status !== 'RESOLVED' ? (
              <form onSubmit={handleResolve} className="space-y-4 text-xs pt-2">
                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    Inspector Verification Outcome:
                  </label>
                  <select
                    value={resolutionOutcome}
                    onChange={(e) => setResolutionOutcome(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg bg-white font-medium"
                  >
                    <option value="DOCUMENTED_ADJUSTMENT_VERIFIED">
                      Documented Transit / Handling Loss Verified (Vouchers Attached)
                    </option>
                    <option value="REGISTER_CLERICAL_ERROR_RECTIFIED">
                      Clerical Register Error Rectified by Dealer
                    </option>
                    <option value="UNACCOUNTED_SHORTFALL_RECOVERED">
                      Unaccounted Shortfall Restocked to PDS Store
                    </option>
                    <option value="REFERRED_TO_STATE_FOOD_COMMISSION">
                      Referred to State Food Commission for In-depth Inquiry
                    </option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    Auditor Notes & Verification Citation:
                  </label>
                  <textarea
                    rows={3}
                    value={investigationNote}
                    onChange={(e) => setInvestigationNote(e.target.value)}
                    placeholder="Enter official voucher numbers, physical count findings, or hearing remarks..."
                    className="w-full p-2.5 border border-gray-300 rounded-lg"
                    required
                  />
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setSelectedDiscrepancy(null)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50"
                  >
                    Close
                  </button>
                  <button
                    type="submit"
                    disabled={resolving}
                    className="px-4 py-2 bg-[#1b5e3a] text-white rounded-lg font-semibold hover:bg-[#164e2e] disabled:opacity-50"
                  >
                    {resolving ? 'Submitting...' : 'Record Verified Resolution'}
                  </button>
                </div>
              </form>
            ) : (
              <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-200 text-emerald-900 text-xs space-y-1">
                <div className="flex items-center gap-1 font-bold">
                  <CheckCircle2 className="w-4 h-4 text-emerald-700" />
                  Case Resolved & Archived
                </div>
                <p>Outcome: {selectedDiscrepancy.investigation_outcome ?? 'Documented adjustment verified.'}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
