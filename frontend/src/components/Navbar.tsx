import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import {
  ShieldCheck,
  Wheat,
  BarChart3,
  UserCheck,
  Bot,
  LogIn,
  LogOut,
  Globe,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="sticky top-0 z-50 bg-[#fcfaf7]/95 backdrop-blur-md border-b border-[#e5dfd5]">
      {/* Top Banner Notice */}
      <div className="bg-[#1b5e3a] text-white text-xs px-4 py-1.5 flex items-center justify-between font-medium">
        <div className="flex items-center gap-2 max-w-7xl mx-auto w-full">
          <span className="inline-flex items-center gap-1 bg-white/20 px-2 py-0.5 rounded text-[11px] font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
            {t('demo_data')}
          </span>
          <span className="truncate">{t('demo_notice')}</span>
          <span className="hidden md:inline text-white/70 ml-auto">
            NFSA Public Allocation Portal Integration Ready
          </span>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Logo and Brand */}
        <Link to="/" className="flex items-center gap-2.5 text-decoration-none group">
          <div className="w-10 h-10 rounded-lg bg-[#1b5e3a] flex items-center justify-center text-white shadow-sm group-hover:bg-[#164e2e] transition-colors">
            <Wheat className="w-6 h-6 text-amber-300" />
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-bold tracking-tight text-[#164e2e] leading-tight">
              {t('app_name')}
            </span>
            <span className="text-[10px] uppercase font-semibold text-gray-500 tracking-wider">
              PDS Intelligence & Audits
            </span>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <nav className="hidden md:flex items-center gap-1 text-sm font-medium">
          <Link
            to="/"
            className={`px-3 py-2 rounded-md transition-colors ${
              isActive('/')
                ? 'bg-[#1b5e3a]/10 text-[#1b5e3a] font-semibold'
                : 'text-gray-700 hover:text-[#1b5e3a] hover:bg-gray-100'
            }`}
          >
            {t('nav_home')}
          </Link>

          <Link
            to="/analytics"
            className={`px-3 py-2 rounded-md transition-colors flex items-center gap-1.5 ${
              isActive('/analytics')
                ? 'bg-[#1b5e3a]/10 text-[#1b5e3a] font-semibold'
                : 'text-gray-700 hover:text-[#1b5e3a] hover:bg-gray-100'
            }`}
          >
            <BarChart3 className="w-4 h-4 text-[#1b5e3a]" />
            {t('nav_analytics')}
          </Link>

          <Link
            to="/beneficiary"
            className={`px-3 py-2 rounded-md transition-colors flex items-center gap-1.5 ${
              isActive('/beneficiary')
                ? 'bg-[#1b5e3a]/10 text-[#1b5e3a] font-semibold'
                : 'text-gray-700 hover:text-[#1b5e3a] hover:bg-gray-100'
            }`}
          >
            <UserCheck className="w-4 h-4 text-[#1b5e3a]" />
            {t('nav_beneficiary')}
          </Link>

          <Link
            to="/audits"
            className={`px-3 py-2 rounded-md transition-colors flex items-center gap-1.5 ${
              isActive('/audits')
                ? 'bg-[#1b5e3a]/10 text-[#1b5e3a] font-semibold'
                : 'text-gray-700 hover:text-[#1b5e3a] hover:bg-gray-100'
            }`}
          >
            <ShieldCheck className="w-4 h-4 text-[#d97706]" />
            {t('nav_audits')}
          </Link>

          <Link
            to="/tinyfish"
            className={`px-3 py-2 rounded-md transition-colors flex items-center gap-1.5 ${
              isActive('/tinyfish')
                ? 'bg-[#1b5e3a]/10 text-[#1b5e3a] font-semibold'
                : 'text-gray-700 hover:text-[#1b5e3a] hover:bg-gray-100'
            }`}
          >
            <Bot className="w-4 h-4 text-emerald-600" />
            <span>{t('nav_tinyfish')}</span>
            <span className="text-[10px] bg-emerald-100 text-emerald-800 font-bold px-1.5 py-0.2 rounded-full">
              AI
            </span>
          </Link>
        </nav>

        {/* Right Section: Language Switcher & User Menu */}
        <div className="flex items-center gap-3">
          {/* Language Switcher */}
          <button
            onClick={() => setLanguage(language === 'en' ? 'hi' : 'en')}
            className="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1.5 rounded-md border border-[#d8d0c5] hover:bg-white text-gray-700 transition-colors cursor-pointer"
            title="Switch Language / भाषा बदलें"
          >
            <Globe className="w-3.5 h-3.5 text-[#1b5e3a]" />
            <span>{language === 'en' ? 'English' : 'हिंदी'}</span>
          </button>

          {/* User profile / Login */}
          {user ? (
            <div className="flex items-center gap-2">
              <div className="hidden sm:flex flex-col text-right">
                <span className="text-xs font-semibold text-gray-800 leading-tight">
                  {user.full_name}
                </span>
                <span className="text-[10px] font-bold text-[#1b5e3a] uppercase">
                  {user.role}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1 text-xs font-medium px-2.5 py-1.5 rounded-md bg-gray-100 hover:bg-red-50 text-gray-700 hover:text-red-700 transition-colors cursor-pointer"
                title={t('nav_logout')}
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{t('nav_logout')}</span>
              </button>
            </div>
          ) : (
            <Link
              to="/login"
              className="flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-md bg-[#1b5e3a] text-white hover:bg-[#164e2e] shadow-xs transition-colors"
            >
              <LogIn className="w-3.5 h-3.5" />
              <span>{t('nav_login')}</span>
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};
