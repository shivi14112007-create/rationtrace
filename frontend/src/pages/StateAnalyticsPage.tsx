import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';
import type {
  OverviewStats,
  StateAnalytics,
  Trend,
  CommodityBreakdown,
} from '../types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';
import {
  BarChart3,
  Table as TableIcon,
  Wheat,
  Calendar,
} from 'lucide-react';

export const StateAnalyticsPage: React.FC = () => {
  const { t } = useLanguage();

  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [statesData, setStatesData] = useState<StateAnalytics[]>([]);
  const [trends, setTrends] = useState<Trend[]>([]);
  const [commodities, setCommodities] = useState<CommodityBreakdown[]>([]);
  const [loading, setLoading] = useState(true);

  // Accessible Table Alternative toggles for each chart
  const [showTableChart1, setShowTableChart1] = useState(false);
  const [showTableChart2, setShowTableChart2] = useState(false);
  const [showTableChart3, setShowTableChart3] = useState(false);

  // Selected State Filter
  const [selectedState, setSelectedState] = useState('ALL');

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.analytics.getOverview(),
      api.analytics.getStates(),
      api.analytics.getTrends(),
      api.analytics.getCommodities(),
    ])
      .then(([oRes, sRes, tRes, cRes]) => {
        setOverview(oRes);
        setStatesData(sRes);
        setTrends(tRes);
        setCommodities(cRes);
      })
      .catch((err) => console.error("Failed to load state analytics:", err))
      .finally(() => setLoading(false));
  }, []);

  const filteredStates = statesData.filter((s) => {
    return selectedState === 'ALL' || s.state === selectedState;
  });

  return (
    <div className="min-h-screen bg-[#fcfaf7] py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header */}
        <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-bold text-gray-900">
                {t('state_analytics_title')}
              </h1>
              <span className="text-xs bg-emerald-100 text-emerald-800 font-bold px-2 py-0.5 rounded-full">
                PUBLIC DOMAIN
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Cross-portal synthesis comparing National Food Security Portal (NFSA) benchmarks with state-level distribution
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 font-semibold">Filter State:</span>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="text-xs py-1.5 px-3 rounded-lg border border-gray-300 bg-white font-medium"
            >
              <option value="ALL">All Recorded States</option>
              {statesData.map((s) => (
                <option key={s.state} value={s.state}>{s.state}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Aggregate Overview Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">{t('total_allocated')}</div>
            <div className="text-2xl font-bold text-gray-900">
              {loading ? '...' : `${overview?.total_allocated_mt ?? 0} MT`}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Authorized grain allocation</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">{t('total_distributed')}</div>
            <div className="text-2xl font-bold text-[#1b5e3a]">
              {loading ? '...' : `${overview?.total_distributed_mt ?? 0} MT`}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Issued to verified cardholders</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">{t('reconciliation_rate')}</div>
            <div className="text-2xl font-bold text-emerald-700">
              {loading ? '...' : `${overview?.reconciliation_rate_pct ?? 0}%`}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Zero-shortfall adherence</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-[#e5dfd5] shadow-xs">
            <div className="text-xs font-semibold text-gray-500 mb-1">{t('active_shops')}</div>
            <div className="text-2xl font-bold text-gray-900">
              {loading ? '...' : overview?.total_shops ?? 0}
            </div>
            <div className="text-[11px] text-gray-500 mt-1">Fair Price Shops monitored</div>
          </div>
        </div>

        {/* Chart 1: State-wise Reported Allocation vs Distribution */}
        <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-gray-100 pb-3">
            <div>
              <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-[#1b5e3a]" />
                {t('allocation_chart')}
              </h2>
              <div className="text-xs text-gray-500 mt-0.5 flex flex-wrap items-center gap-2">
                <span>Unit: <strong>Metric Tonnes (MT)</strong></span>
                <span>• Period: <strong>2026-09</strong></span>
                <span>• Source: <strong>NFSA Allocation & State e-PDS Portals</strong></span>
              </div>
            </div>

            <button
              onClick={() => setShowTableChart1(!showTableChart1)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors cursor-pointer"
            >
              <TableIcon className="w-3.5 h-3.5 text-[#1b5e3a]" />
              <span>{showTableChart1 ? t('toggle_chart') : t('toggle_table')}</span>
            </button>
          </div>

          {showTableChart1 ? (
            /* Accessible Table Alternative */
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#fcfaf7] border-y border-[#e5dfd5] text-gray-600 font-semibold">
                  <tr>
                    <th className="py-2.5 px-3">State</th>
                    <th className="py-2.5 px-3">Allocated Qty (MT)</th>
                    <th className="py-2.5 px-3">Distributed Qty (MT)</th>
                    <th className="py-2.5 px-3">Variance</th>
                    <th className="py-2.5 px-3">Shops Count</th>
                    <th className="py-2.5 px-3">Reconciliation Compliance</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {filteredStates.map((s) => (
                    <tr key={s.state} className="hover:bg-gray-50/60">
                      <td className="py-2.5 px-3 font-semibold text-gray-900">{s.state}</td>
                      <td className="py-2.5 px-3 font-mono">{s.allocated_quantity}</td>
                      <td className="py-2.5 px-3 font-mono">{s.distributed_quantity}</td>
                      <td className="py-2.5 px-3 font-mono font-bold text-gray-700">
                        {roundTwo(s.distributed_quantity - s.allocated_quantity)} MT
                      </td>
                      <td className="py-2.5 px-3">{s.shops_count}</td>
                      <td className="py-2.5 px-3 font-bold text-emerald-700">
                        {s.compliance_rate_pct}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="h-72 w-full pt-4">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={filteredStates} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0ebe1" />
                  <XAxis dataKey="state" tick={{ fontSize: 12, fill: '#4b5563' }} />
                  <YAxis tick={{ fontSize: 12, fill: '#4b5563' }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#fff', borderColor: '#e5dfd5', borderRadius: 8, fontSize: 12 }}
                  />
                  <Legend wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
                  <Bar dataKey="allocated_quantity" name="Allocated (MT)" fill="#d97706" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="distributed_quantity" name="Distributed (MT)" fill="#1b5e3a" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Provenance Box */}
          <div className="text-[11px] text-gray-500 bg-[#fcfaf7] p-2.5 rounded-lg border border-gray-200">
            <strong>{t('data_provenance')}:</strong> Cross-verified with National Food Security Act (NFSA) allocation tables and state e-PoS machine transmissions. Ref: <code>NFSA_ALLOC_2026_09</code>.
          </div>
        </div>

        {/* Grid: Chart 2 (Monthly Trends) & Chart 3 (Commodity Share) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Chart 2: Monthly Trends */}
          <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-gray-900 flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-[#1b5e3a]" />
                  {t('trends_chart')}
                </h3>
                <span className="text-[11px] text-gray-500">Unit: Metric Tonnes (MT)</span>
              </div>
              <button
                onClick={() => setShowTableChart2(!showTableChart2)}
                className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded bg-gray-100 hover:bg-gray-200 text-gray-700 cursor-pointer"
              >
                <TableIcon className="w-3 h-3 text-[#1b5e3a]" />
                <span>{showTableChart2 ? 'Chart' : 'Table'}</span>
              </button>
            </div>

            {showTableChart2 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#fcfaf7] border-y border-[#e5dfd5] text-gray-600 font-semibold">
                    <tr>
                      <th className="py-2 px-3">Period</th>
                      <th className="py-2 px-3">Allocated (MT)</th>
                      <th className="py-2 px-3">Distributed (MT)</th>
                      <th className="py-2 px-3">Flagged Discrepancies</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {trends.map((tr) => (
                      <tr key={tr.period} className="hover:bg-gray-50/60">
                        <td className="py-2 px-3 font-semibold">{tr.period}</td>
                        <td className="py-2 px-3 font-mono">{tr.allocated}</td>
                        <td className="py-2 px-3 font-mono">{tr.distributed}</td>
                        <td className="py-2 px-3 font-mono font-bold text-amber-700">{tr.discrepancy_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="h-64 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={trends} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0ebe1" />
                    <XAxis dataKey="period" tick={{ fontSize: 11, fill: '#4b5563' }} />
                    <YAxis tick={{ fontSize: 11, fill: '#4b5563' }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#fff', borderColor: '#e5dfd5', borderRadius: 8, fontSize: 12 }}
                    />
                    <Legend wrapperStyle={{ fontSize: 11, paddingTop: 6 }} />
                    <Line type="monotone" dataKey="allocated" name="Allocated (MT)" stroke="#d97706" strokeWidth={2} />
                    <Line type="monotone" dataKey="distributed" name="Distributed (MT)" stroke="#1b5e3a" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Chart 3: Commodity Share & Variance */}
          <div className="bg-white p-6 rounded-2xl border border-[#e5dfd5] shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <div>
                <h3 className="text-base font-bold text-gray-900 flex items-center gap-1.5">
                  <Wheat className="w-4 h-4 text-[#1b5e3a]" />
                  {t('commodity_chart')}
                </h3>
                <span className="text-[11px] text-gray-500">Breakdown: Rice, Wheat, Coarse Grains</span>
              </div>
              <button
                onClick={() => setShowTableChart3(!showTableChart3)}
                className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded bg-gray-100 hover:bg-gray-200 text-gray-700 cursor-pointer"
              >
                <TableIcon className="w-3 h-3 text-[#1b5e3a]" />
                <span>{showTableChart3 ? 'Chart' : 'Table'}</span>
              </button>
            </div>

            {showTableChart3 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-[#fcfaf7] border-y border-[#e5dfd5] text-gray-600 font-semibold">
                    <tr>
                      <th className="py-2 px-3">Commodity</th>
                      <th className="py-2 px-3">Allocated ({commodities[0]?.unit ?? 'MT'})</th>
                      <th className="py-2 px-3">Distributed ({commodities[0]?.unit ?? 'MT'})</th>
                      <th className="py-2 px-3">Variance (%)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {commodities.map((c) => (
                      <tr key={c.commodity} className="hover:bg-gray-50/60">
                        <td className="py-2 px-3 font-semibold">{c.commodity}</td>
                        <td className="py-2 px-3 font-mono">{c.allocated}</td>
                        <td className="py-2 px-3 font-mono">{c.distributed}</td>
                        <td className="py-2 px-3 font-mono font-bold text-gray-700">{c.variance_pct}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="h-64 w-full pt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={commodities} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f0ebe1" />
                    <XAxis dataKey="commodity" tick={{ fontSize: 11, fill: '#4b5563' }} />
                    <YAxis tick={{ fontSize: 11, fill: '#4b5563' }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#fff', borderColor: '#e5dfd5', borderRadius: 8, fontSize: 12 }}
                    />
                    <Legend wrapperStyle={{ fontSize: 11, paddingTop: 6 }} />
                    <Bar dataKey="allocated" name="Allocated (MT)" fill="#2563eb" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="distributed" name="Distributed (MT)" fill="#059669" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

function roundTwo(num: number): number {
  return Math.round(num * 100) / 100;
}
