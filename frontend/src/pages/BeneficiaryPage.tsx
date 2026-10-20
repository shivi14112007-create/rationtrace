import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';
import type {
  BeneficiaryMeResponse,
  Transaction,
  EntitlementsResponse,
  Complaint,
} from '../types';
import {
  UserCheck,
  Wheat,
  Scale,
  AlertCircle,
  Clock,
  PlusCircle,
  FileCheck2,
  CheckCircle2,
  Search,
  Check,
  X
} from 'lucide-react';

export const BeneficiaryPage: React.FC = () => {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [profileData, setProfileData] = useState<BeneficiaryMeResponse | null>(null);
  const [entitlements, setEntitlements] = useState<EntitlementsResponse | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [commodityFilter, setCommodityFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  // Complaint Modal State
  const [showComplaintModal, setShowComplaintModal] = useState(false);
  const [complaintCategory, setComplaintCategory] = useState('UNDER_DISTRIBUTION');
  const [complaintShopId, setComplaintShopId] = useState<number>(1);
  const [complaintDescription, setComplaintDescription] = useState('');
  const [submittingComplaint, setSubmittingComplaint] = useState(false);
  const [complaintSuccessRef, setComplaintSuccessRef] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [pRes, eRes, tRes, cRes] = await Promise.all([
        api.beneficiary.getMe(),
        api.beneficiary.getEntitlements(),
        api.beneficiary.getTransactions(50),
        api.complaints.getComplaints(),
      ]);
      setProfileData(pRes);
      setEntitlements(eRes);
      setTransactions(tRes);
      setComplaints(cRes);
      if (pRes.profile?.assigned_shop_id) {
        setComplaintShopId(pRes.profile.assigned_shop_id);
      }
    } catch (err) {
      console.error("Failed to load beneficiary data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateComplaint = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!complaintDescription.trim()) return;

    setSubmittingComplaint(true);
    try {
      const newComplaint = await api.complaints.createComplaint({
        related_shop_id: complaintShopId,
        category: complaintCategory,
        description: complaintDescription,
      });
      setComplaintSuccessRef(newComplaint.reference_number);
      setComplaintDescription('');
      // Reload complaints
      const updatedComplaints = await api.complaints.getComplaints();
      setComplaints(updatedComplaints);
    } catch (err: any) {
      alert(`Failed to submit complaint: ${err.message}`);
    } finally {
      setSubmittingComplaint(false);
    }
  };

  const filteredTransactions = transactions.filter((tx) => {
    const matchesCommodity = commodityFilter === 'ALL' || tx.commodity.toUpperCase() === commodityFilter;
    const matchesSearch =
      tx.commodity.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tx.shop_identifier.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tx.reporting_period.includes(searchQuery);
    return matchesCommodity && matchesSearch;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-[#fcfaf7] flex items-center justify-center py-12">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-[#1b5e3a] border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-xs font-semibold text-gray-600">Loading beneficiary records...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#fcfaf7] py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header Profile Bar */}
        <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-[#1b5e3a] flex items-center justify-center text-white shadow-xs">
              <UserCheck className="w-8 h-8 text-amber-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
                  {profileData?.user?.full_name ?? user?.full_name ?? 'Sunita Devi'}
                </h1>
                <span className="text-xs bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
                  {profileData?.profile?.ration_card_type ?? 'PHH'} CARD
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {t('masked_id')}: <strong className="font-mono text-gray-700">{profileData?.profile?.masked_beneficiary_identifier ?? 'BEN-DL-98214'}</strong> • {profileData?.profile?.state ?? 'Delhi'} ({profileData?.profile?.district ?? 'South Delhi'})
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="text-xs text-right hidden sm:block">
              <span className="text-gray-500 block">Assigned FPS:</span>
              <strong className="text-gray-900">{profileData?.profile?.assigned_shop_name ?? 'Manoj Ration Kendra (Shop #142)'}</strong>
            </div>
            <button
              onClick={() => {
                setShowComplaintModal(true);
                setComplaintSuccessRef(null);
              }}
              className="w-full md:w-auto flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[#d97706] hover:bg-[#b45309] text-white text-xs font-bold shadow-xs transition-all cursor-pointer"
            >
              <PlusCircle className="w-4 h-4" />
              <span>{t('report_discrepancy')}</span>
            </button>
          </div>
        </div>

        {/* Section 1: Entitlement vs Distribution Comparison */}
        <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <div>
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Scale className="w-5 h-5 text-[#1b5e3a]" />
                {t('entitlements_heading')}
              </h2>
              <p className="text-xs text-gray-500">
                Official quota vs quantity recorded as issued for period: <strong>{entitlements?.reporting_period ?? '2026-09'}</strong>
              </p>
            </div>
            <span className="text-[11px] font-semibold bg-gray-100 text-gray-600 px-2.5 py-1 rounded">
              Verified Source: Delhi PDS Portal
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            {entitlements?.items?.map((item, idx) => {
              const isShortfall = item.variance < 0;
              return (
                <div
                  key={idx}
                  className={`p-4 rounded-xl border ${
                    isShortfall ? 'border-amber-300 bg-amber-50/40' : 'border-[#e5dfd5] bg-[#fcfaf7]'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-gray-900 text-sm flex items-center gap-1.5">
                      <Wheat className="w-4 h-4 text-[#1b5e3a]" />
                      {item.commodity}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        isShortfall ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-800'
                      }`}
                    >
                      {item.status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs py-2 border-t border-b border-gray-200/60 my-2">
                    <div>
                      <span className="text-gray-500 block text-[11px]">{t('entitled_qty')}</span>
                      <strong className="text-gray-900 text-sm">{item.entitlement_quantity} {item.unit}</strong>
                    </div>
                    <div>
                      <span className="text-gray-500 block text-[11px]">{t('recorded_qty')}</span>
                      <strong className="text-gray-900 text-sm">{item.recorded_quantity} {item.unit}</strong>
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-600 font-medium">{t('variance')}:</span>
                    <span className={`font-bold ${isShortfall ? 'text-amber-700' : 'text-emerald-700'}`}>
                      {item.variance > 0 ? `+${item.variance}` : item.variance} {item.unit}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Section 2: Distribution Transaction Ledger */}
        <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <FileCheck2 className="w-5 h-5 text-[#1b5e3a]" />
                {t('transactions_heading')}
              </h2>
              <p className="text-xs text-gray-500">
                Official electronic distribution slip records linked to your ration card
              </p>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Filter transactions..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="text-xs pl-8 pr-3 py-1.5 rounded-lg border border-gray-300 bg-white focus:outline-none focus:ring-1 focus:ring-[#1b5e3a]"
                />
              </div>

              <select
                value={commodityFilter}
                onChange={(e) => setCommodityFilter(e.target.value)}
                className="text-xs py-1.5 px-2.5 rounded-lg border border-gray-300 bg-white font-medium"
              >
                <option value="ALL">All Commodities</option>
                <option value="WHEAT">Wheat</option>
                <option value="RICE">Rice</option>
                <option value="SUGAR">Sugar</option>
              </select>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#fcfaf7] border-y border-[#e5dfd5] text-gray-600 font-semibold">
                <tr>
                  <th className="py-2.5 px-3">Transaction Date</th>
                  <th className="py-2.5 px-3">Reporting Period</th>
                  <th className="py-2.5 px-3">{t('commodity')}</th>
                  <th className="py-2.5 px-3">{t('recorded_qty')}</th>
                  <th className="py-2.5 px-3">{t('entitled_qty')}</th>
                  <th className="py-2.5 px-3">Shop Center</th>
                  <th className="py-2.5 px-3">Audit Match</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredTransactions.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="py-6 text-center text-gray-400">
                      No distribution transactions match your filter criteria.
                    </td>
                  </tr>
                ) : (
                  filteredTransactions.map((tx) => {
                    const isDiscrepant = tx.recorded_quantity < tx.entitlement_quantity;
                    return (
                      <tr key={tx.id} className="hover:bg-gray-50/60 transition-colors">
                        <td className="py-3 px-3 font-medium text-gray-800">
                          {new Date(tx.transaction_date).toLocaleDateString()}
                        </td>
                        <td className="py-3 px-3 text-gray-600">{tx.reporting_period}</td>
                        <td className="py-3 px-3 font-semibold text-gray-900">{tx.commodity}</td>
                        <td className="py-3 px-3 font-bold text-gray-900">
                          {tx.recorded_quantity} {tx.unit}
                        </td>
                        <td className="py-3 px-3 text-gray-500">
                          {tx.entitlement_quantity} {tx.unit}
                        </td>
                        <td className="py-3 px-3 text-gray-600">
                          <span className="font-mono text-[11px] block">{tx.shop_identifier}</span>
                          <span className="text-[10px] text-gray-400 truncate max-w-[120px] block">{tx.shop_name}</span>
                        </td>
                        <td className="py-3 px-3">
                          {isDiscrepant ? (
                            <span className="inline-flex items-center gap-1 text-amber-700 font-bold bg-amber-50 px-2 py-0.5 rounded text-[11px]">
                              <AlertCircle className="w-3 h-3" />
                              Shortfall (-{tx.entitlement_quantity - tx.recorded_quantity} kg)
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded text-[11px]">
                              <CheckCircle2 className="w-3 h-3" />
                              Balanced
                            </span>
                          )}
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Section 3: Grievance Redressal Trackers */}
        <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Clock className="w-5 h-5 text-[#d97706]" />
                {t('track_complaints')}
              </h2>
              <p className="text-xs text-gray-500">
                Auditable grievance tickets submitted to the official review team
              </p>
            </div>
            <span className="text-xs font-semibold text-gray-600">
              Total Filed: {complaints.length}
            </span>
          </div>

          <div className="space-y-3 pt-2">
            {complaints.length === 0 ? (
              <div className="p-8 text-center bg-[#fcfaf7] rounded-xl border border-dashed border-gray-300 text-gray-500 text-xs">
                No active complaints filed. Click "Report a Discrepancy" if you noticed an entitlement shortfall.
              </div>
            ) : (
              complaints.map((c) => (
                <div key={c.id} className="p-4 rounded-xl border border-gray-200 bg-[#fcfaf7] space-y-2">
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold bg-gray-200 text-gray-800 px-2 py-0.5 rounded">
                        {c.reference_number}
                      </span>
                      <span className="text-xs font-bold text-gray-800">
                        {c.category.replace(/_/g, ' ')}
                      </span>
                    </div>

                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        c.status === 'RESOLVED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : c.status === 'INVESTIGATION'
                          ? 'bg-purple-100 text-purple-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {c.status}
                    </span>
                  </div>

                  <p className="text-xs text-gray-700 leading-relaxed">{c.description}</p>

                  {c.resolution_summary && (
                    <div className="p-2.5 rounded bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs mt-2">
                      <strong>Resolution Note:</strong> {c.resolution_summary}
                    </div>
                  )}

                  {/* Investigation Event Timeline */}
                  {c.events && c.events.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200/80">
                      <span className="text-[11px] font-semibold text-gray-500 block mb-1.5">
                        Investigation Timeline:
                      </span>
                      <div className="space-y-1.5">
                        {c.events.map((ev) => (
                          <div key={ev.id} className="text-[11px] text-gray-600 flex items-start gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-[#1b5e3a] mt-1 shrink-0"></span>
                            <div>
                              <strong className="text-gray-800">{ev.event_type.replace(/_/g, ' ')}</strong>: {ev.note}{' '}
                              <span className="text-gray-400">({ev.actor_name})</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Report Discrepancy Modal */}
      {showComplaintModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-gray-200 space-y-4">
            <div className="flex items-center justify-between border-b pb-3">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-[#d97706]" />
                {t('file_complaint')}
              </h3>
              <button
                onClick={() => setShowComplaintModal(false)}
                className="text-gray-400 hover:text-gray-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {complaintSuccessRef ? (
              <div className="p-6 text-center space-y-4">
                <div className="w-12 h-12 bg-emerald-100 text-emerald-800 rounded-full flex items-center justify-center mx-auto">
                  <Check className="w-6 h-6" />
                </div>
                <h4 className="text-base font-bold text-gray-900">
                  Grievance Filed Successfully
                </h4>
                <p className="text-xs text-gray-600">
                  Your complaint reference number is:
                </p>
                <div className="font-mono text-lg font-extrabold text-[#1b5e3a] bg-emerald-50 p-2 rounded-lg border border-emerald-200">
                  {complaintSuccessRef}
                </div>
                <p className="text-[11px] text-gray-500">
                  Assigned to the local PDS Inspectorate. You can track investigation notes in the tracker above.
                </p>
                <button
                  onClick={() => setShowComplaintModal(false)}
                  className="px-5 py-2 bg-[#1b5e3a] text-white text-xs font-semibold rounded-lg hover:bg-[#164e2e]"
                >
                  Done
                </button>
              </div>
            ) : (
              <form onSubmit={handleCreateComplaint} className="space-y-4 text-xs">
                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    {t('complaint_category')}
                  </label>
                  <select
                    value={complaintCategory}
                    onChange={(e) => setComplaintCategory(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg bg-white"
                  >
                    <option value="UNDER_DISTRIBUTION">{t('category_under')}</option>
                    <option value="NON_ISSUANCE">{t('category_non')}</option>
                    <option value="OVERCHARGE">{t('category_overcharge')}</option>
                    <option value="QUALITY_ISSUE">{t('category_quality')}</option>
                    <option value="SHOP_CLOSED">{t('category_shop_closed')}</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    Target Fair Price Shop
                  </label>
                  <input
                    type="text"
                    disabled
                    value={profileData?.profile?.assigned_shop_name ?? 'Manoj Ration Kendra (Shop #142)'}
                    className="w-full p-2 border border-gray-200 rounded-lg bg-gray-50 text-gray-600"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-gray-700 mb-1">
                    {t('description')}
                  </label>
                  <textarea
                    rows={4}
                    value={complaintDescription}
                    onChange={(e) => setComplaintDescription(e.target.value)}
                    placeholder="Provide exact details (e.g., received only 16 kg of wheat instead of 20 kg entitlement on 12th Sept)..."
                    className="w-full p-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-[#1b5e3a]"
                    required
                  />
                </div>

                <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-amber-800 text-[11px] leading-relaxed">
                  <strong>Notice:</strong> RationTrace complaints generate audit review requests. Submitting
                  false claims may delay resolution of genuine citizen grievances.
                </div>

                <div className="flex items-center justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setShowComplaintModal(false)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50"
                  >
                    {t('cancel')}
                  </button>
                  <button
                    type="submit"
                    disabled={submittingComplaint}
                    className="px-4 py-2 bg-[#1b5e3a] text-white rounded-lg font-semibold hover:bg-[#164e2e] disabled:opacity-50"
                  >
                    {submittingComplaint ? 'Submitting...' : t('submit_complaint')}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
