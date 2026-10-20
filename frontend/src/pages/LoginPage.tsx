import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { Wheat, Lock, User as UserIcon, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please provide both username and password.');
      return;
    }

    setError(null);
    setLoading(true);
    try {
      const user = await login(username, password);
      if (user.role === 'BENEFICIARY') {
        navigate('/beneficiary');
      } else if (user.role === 'OFFICIAL' || user.role === 'ADMIN') {
        navigate('/audits');
      } else {
        navigate('/analytics');
      }
    } catch (err: any) {
      setError(err.message || 'Invalid credentials. Please verify your username and password.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setError(null);
  };

  return (
    <div className="min-h-[calc(100vh-140px)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-[#fcfaf7]">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl border border-[#e5dfd5] shadow-sm">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-xl bg-[#1b5e3a] flex items-center justify-center text-white mx-auto shadow-xs">
            <Wheat className="w-7 h-7 text-amber-300" />
          </div>
          <h2 className="text-2xl font-extrabold text-gray-900">
            {t('login_title')}
          </h2>
          <p className="text-xs text-gray-500">
            Access your authorized public distribution and grievance dashboard
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form className="mt-8 space-y-4" onSubmit={handleLogin}>
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              {t('username')}
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                <UserIcon className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. beneficiary_demo"
                className="block w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#1b5e3a] focus:border-transparent"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">
              {t('password')}
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-400">
                <Lock className="w-4 h-4" />
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="block w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg text-sm bg-white focus:outline-none focus:ring-2 focus:ring-[#1b5e3a] focus:border-transparent"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center items-center gap-2 py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-[#1b5e3a] hover:bg-[#164e2e] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#1b5e3a] transition-all cursor-pointer disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : t('nav_login')}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Demo Roles 1-Click Fill */}
        <div className="pt-6 border-t border-gray-200">
          <div className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3 text-center">
            {t('demo_accounts')}
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <button
              type="button"
              onClick={() => handleQuickLogin('beneficiary_demo', 'Demo123!')}
              className="p-2.5 rounded-lg border border-emerald-200 bg-emerald-50/50 hover:bg-emerald-100/60 text-left transition-colors cursor-pointer"
            >
              <div className="font-bold text-emerald-900">{t('role_beneficiary')}</div>
              <div className="text-[10px] text-emerald-700">beneficiary_demo</div>
            </button>

            <button
              type="button"
              onClick={() => handleQuickLogin('official_demo', 'Demo123!')}
              className="p-2.5 rounded-lg border border-amber-200 bg-amber-50/50 hover:bg-amber-100/60 text-left transition-colors cursor-pointer"
            >
              <div className="font-bold text-amber-900">{t('role_official')}</div>
              <div className="text-[10px] text-amber-700">official_demo</div>
            </button>

            <button
              type="button"
              onClick={() => handleQuickLogin('dealer_demo', 'Demo123!')}
              className="p-2.5 rounded-lg border border-blue-200 bg-blue-50/50 hover:bg-blue-100/60 text-left transition-colors cursor-pointer"
            >
              <div className="font-bold text-blue-900">{t('role_dealer')}</div>
              <div className="text-[10px] text-blue-700">dealer_demo</div>
            </button>

            <button
              type="button"
              onClick={() => handleQuickLogin('admin_demo', 'Demo123!')}
              className="p-2.5 rounded-lg border border-purple-200 bg-purple-50/50 hover:bg-purple-100/60 text-left transition-colors cursor-pointer"
            >
              <div className="font-bold text-purple-900">{t('role_admin')}</div>
              <div className="text-[10px] text-purple-700">admin_demo</div>
            </button>
          </div>
        </div>

        {/* Security badge */}
        <div className="text-[11px] text-gray-500 text-center flex items-center justify-center gap-1">
          <ShieldCheck className="w-3.5 h-3.5 text-[#1b5e3a]" />
          <span>Role-Based Access Control • Demo Environment Active</span>
        </div>
      </div>
    </div>
  );
};
