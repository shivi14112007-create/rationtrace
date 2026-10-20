import React from 'react';
import { Wheat, ShieldCheck, ExternalLink } from 'lucide-react';

export const Footer: React.FC = () => {

  return (
    <footer className="bg-[#1b2b21] text-gray-300 border-t border-[#294233] mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Column 1: Brand & Mission */}
          <div className="md:col-span-2 space-y-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-[#276e48] flex items-center justify-center text-white">
                <Wheat className="w-5 h-5 text-amber-300" />
              </div>
              <span className="text-xl font-bold tracking-tight text-white">
                RationTrace
              </span>
            </div>
            <p className="text-sm text-gray-300/80 leading-relaxed max-w-md">
              Evidence-based public food security reconciliation platform. Built on the core principle of
              transparency without unsupported accusations, clear data provenance, and verifiable audit reconciliation.
            </p>
            <div className="text-xs text-amber-400/90 bg-[#273d30] p-3 rounded-md border border-[#3b5946] leading-relaxed">
              <strong>Data Integrity Notice:</strong> All metrics display extraction timestamps and provenance.
              Demonstration records are explicitly identified to prevent confusion with official government orders.
            </div>
          </div>

          {/* Column 2: Public Data Sources */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
              Official Portals
            </h4>
            <ul className="space-y-2 text-xs">
              <li>
                <a
                  href="https://nfsa.gov.in"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-amber-300 flex items-center gap-1 transition-colors"
                >
                  National Food Security Portal <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href="https://nfsa.gov.in/public/nfsadashboard/PublicAllocationDashboard.aspx"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-amber-300 flex items-center gap-1 transition-colors"
                >
                  NFSA Allocation Dashboard <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href="https://impds.nic.in"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-amber-300 flex items-center gap-1 transition-colors"
                >
                  IMPDS National Portal <ExternalLink className="w-3 h-3" />
                </a>
              </li>
              <li>
                <a
                  href="https://docs.tinyfish.ai"
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-amber-300 flex items-center gap-1 transition-colors"
                >
                  TinyFish Web Agent Docs <ExternalLink className="w-3 h-3" />
                </a>
              </li>
            </ul>
          </div>

          {/* Column 3: Platform Sections */}
          <div>
            <h4 className="text-sm font-semibold text-white uppercase tracking-wider mb-3">
              Platform
            </h4>
            <ul className="space-y-2 text-xs">
              <li><span className="text-gray-400">Rule A: Stock Reconciliation</span></li>
              <li><span className="text-gray-400">Rule B: Negative Balance Detection</span></li>
              <li><span className="text-gray-400">Grievance Audit Redressal</span></li>
              <li><span className="text-gray-400">TinyFish Autonomous Intelligence</span></li>
              <li><span className="text-gray-400">Accessible Tabular Alternatives</span></li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-[#294233] flex flex-col sm:flex-row justify-between items-center text-xs text-gray-400 gap-2">
          <p>© 2026 RationTrace Intelligence Platform. For food security transparency.</p>
          <div className="flex items-center gap-4">
            <span className="inline-flex items-center gap-1 text-emerald-400">
              <ShieldCheck className="w-3.5 h-3.5" />
              Role-Based Authorization Active
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
