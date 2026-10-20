import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../services/api';
import type { OverviewStats } from '../types';
import {
  Scale,
  Bot,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Building2,
  Users,
  Lock
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { t } = useLanguage();
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    api.analytics.getOverview()
      .then(setStats)
      .catch((err) => console.error("Failed to load overview stats:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-col min-h-screen bg-[#fcfaf7]">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 border-b border-[#e8e2d8]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto space-y-6">
            {/* Status Pill */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#1b5e3a]/10 border border-[#1b5e3a]/20 text-[#1b5e3a] text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>{t('demo_data')} • NFSA 2026-09 Dataset</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-[#111827] tracking-tight leading-tight">
              {t('hero_title')}
            </h1>

            <p className="text-lg sm:text-xl text-gray-600 leading-relaxed">
              {t('hero_subtitle')}
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <Link
                to="/analytics"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[#1b5e3a] text-white font-semibold shadow-md hover:bg-[#164e2e] transition-all"
              >
                <span>{t('explore_dashboard')}</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/beneficiary"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-white border border-[#d3cac0] text-gray-800 font-semibold hover:bg-gray-50 transition-all shadow-xs"
              >
                <span>{t('view_beneficiary_records')}</span>
              </Link>
              <Link
                to="/tinyfish"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-[#fff8eb] border border-[#f3d9a2] text-[#b45309] font-semibold hover:bg-[#ffedd5] transition-all shadow-xs"
              >
                <Bot className="w-4 h-4 text-[#d97706]" />
                <span>{t('nav_tinyfish')}</span>
              </Link>
            </div>
          </div>

          {/* Quick Metrics Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-16 max-w-5xl mx-auto">
            <div className="bg-white p-5 rounded-xl border border-[#e8e2d8] shadow-xs">
              <div className="flex items-center gap-2 text-gray-500 text-xs font-semibold mb-1">
                <Building2 className="w-4 h-4 text-[#1b5e3a]" />
                <span>Fair Price Shops</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {loading ? '...' : stats?.total_shops ?? '3'}
              </div>
              <div className="text-[11px] text-gray-500 mt-1">Delhi & Bihar PDS</div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-[#e8e2d8] shadow-xs">
              <div className="flex items-center gap-2 text-gray-500 text-xs font-semibold mb-1">
                <Users className="w-4 h-4 text-[#1b5e3a]" />
                <span>Beneficiaries</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {loading ? '...' : stats?.total_beneficiaries ?? '1,240'}
              </div>
              <div className="text-[11px] text-gray-500 mt-1">PHH & AAY Households</div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-[#e8e2d8] shadow-xs">
              <div className="flex items-center gap-2 text-gray-500 text-xs font-semibold mb-1">
                <Scale className="w-4 h-4 text-[#1b5e3a]" />
                <span>Reconciliation Rate</span>
              </div>
              <div className="text-2xl font-bold text-emerald-700">
                {loading ? '...' : `${stats?.reconciliation_rate_pct ?? '92.4'}%`}
              </div>
              <div className="text-[11px] text-gray-500 mt-1">Mathematical Stock Match</div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-[#e8e2d8] shadow-xs">
              <div className="flex items-center gap-2 text-gray-500 text-xs font-semibold mb-1">
                <AlertTriangle className="w-4 h-4 text-[#d97706]" />
                <span>Flagged Inconsistencies</span>
              </div>
              <div className="text-2xl font-bold text-amber-600">
                {loading ? '...' : stats?.open_discrepancies_count ?? '2'}
              </div>
              <div className="text-[11px] text-gray-500 mt-1">Rule A & B Anomalies</div>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works Section */}
      <section className="py-16 bg-white border-b border-[#e8e2d8]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">
              {t('how_it_works')}
            </h2>
            <p className="text-sm text-gray-600 mt-2">
              Three-pillar architecture designed for verifiable food distribution integrity.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-xl border border-[#e8e2d8] bg-[#fcfaf7] space-y-3">
              <div className="w-10 h-10 rounded-lg bg-[#1b5e3a]/10 flex items-center justify-center text-[#1b5e3a]">
                <Bot className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">{t('step1_title')}</h3>
              <p className="text-sm text-gray-600 leading-relaxed">{t('step1_desc')}</p>
            </div>

            <div className="p-6 rounded-xl border border-[#e8e2d8] bg-[#fcfaf7] space-y-3">
              <div className="w-10 h-10 rounded-lg bg-[#d97706]/10 flex items-center justify-center text-[#d97706]">
                <Scale className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">{t('step2_title')}</h3>
              <p className="text-sm text-gray-600 leading-relaxed">{t('step2_desc')}</p>
            </div>

            <div className="p-6 rounded-xl border border-[#e8e2d8] bg-[#fcfaf7] space-y-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center text-emerald-800">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">{t('step3_title')}</h3>
              <p className="text-sm text-gray-600 leading-relaxed">{t('step3_desc')}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Role Feature Highlights */}
      <section className="py-16 bg-[#fcfaf7] border-b border-[#e8e2d8]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* For Beneficiaries */}
            <div className="bg-white p-6 rounded-xl border border-[#e8e2d8] shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-xs uppercase font-bold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded">
                  Citizens & Beneficiaries
                </span>
                <h4 className="text-lg font-bold text-gray-900 mt-3 mb-2">
                  Entitlement Ledger & Grievances
                </h4>
                <ul className="text-xs text-gray-600 space-y-2 mb-6">
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#1b5e3a]" />
                    Compare expected quota vs recorded grain issuance
                  </li>
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#1b5e3a]" />
                    File shortage or overcharging discrepancy reports
                  </li>
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#1b5e3a]" />
                    Track unique complaint reference timeline
                  </li>
                </ul>
              </div>
              <Link
                to="/beneficiary"
                className="text-xs font-semibold text-[#1b5e3a] hover:text-[#164e2e] flex items-center gap-1"
              >
                Access Beneficiary Portal <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {/* For Officials */}
            <div className="bg-white p-6 rounded-xl border border-[#e8e2d8] shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-xs uppercase font-bold text-amber-800 bg-amber-50 px-2 py-0.5 rounded">
                  PDS Inspectors & Officials
                </span>
                <h4 className="text-lg font-bold text-gray-900 mt-3 mb-2">
                  Stock Audit & Investigation Queue
                </h4>
                <ul className="text-xs text-gray-600 space-y-2 mb-6">
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#d97706]" />
                    Automated Rule A shortfall and surplus detection
                  </li>
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#d97706]" />
                    Negative closing balance flags with formulas
                  </li>
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#d97706]" />
                    Auditable event trail with documented review notes
                  </li>
                </ul>
              </div>
              <Link
                to="/audits"
                className="text-xs font-semibold text-[#d97706] hover:text-amber-800 flex items-center gap-1"
              >
                Open Audit Dashboard <ArrowRight className="w-3 h-3" />
              </Link>
            </div>

            {/* For State Analysts */}
            <div className="bg-white p-6 rounded-xl border border-[#e8e2d8] shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-xs uppercase font-bold text-blue-800 bg-blue-50 px-2 py-0.5 rounded">
                  Public & Policy Analysts
                </span>
                <h4 className="text-lg font-bold text-gray-900 mt-3 mb-2">
                  Cross-Portal State Analytics
                </h4>
                <ul className="text-xs text-gray-600 space-y-2 mb-6">
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                    Multi-state grain allocation and distribution trends
                  </li>
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                    Commodity share analysis (Rice, Wheat, Coarse Grains)
                  </li>
                  <li className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5 text-blue-600" />
                    Accessible tabular alternative for every chart
                  </li>
                </ul>
              </div>
              <Link
                to="/analytics"
                className="text-xs font-semibold text-blue-700 hover:text-blue-900 flex items-center gap-1"
              >
                View State Analytics <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Data Limitation and Ethics Notice */}
      <section className="py-12 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-3">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-gray-600 uppercase tracking-wide">
            <Lock className="w-4 h-4 text-[#1b5e3a]" />
            Privacy & Non-Defamation Commitment
          </div>
          <h3 className="text-xl font-bold text-gray-900">
            Evidence-Based Transparency Without Accusations
          </h3>
          <p className="text-xs text-gray-500 leading-relaxed">
            RationTrace operates strictly as a mathematical auditing and data synthesis tool. An anomaly or
            discrepancy flag indicates a record-keeping variance requiring human inspection, NOT confirmed malfeasance.
            Personal beneficiary numbers are strictly masked, and public portals are accessed in strict adherence
            to public data access guidelines.
          </p>
        </div>
      </section>
    </div>
  );
};
