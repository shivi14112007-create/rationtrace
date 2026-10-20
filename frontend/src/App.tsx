import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './context/LanguageContext';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Footer } from './components/Footer';
import {
  LandingPage,
  LoginPage,
  BeneficiaryPage,
  OfficialAuditPage,
  StateAnalyticsPage,
  TinyFishIntelligencePage,
} from './pages';

export function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <BrowserRouter>
          <div className="flex flex-col min-h-screen bg-[#fcfaf7] text-gray-900 font-sans selection:bg-[#1b5e3a] selection:text-white">
            <Navbar />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/beneficiary" element={<BeneficiaryPage />} />
                <Route path="/audits" element={<OfficialAuditPage />} />
                <Route path="/analytics" element={<StateAnalyticsPage />} />
                <Route path="/tinyfish" element={<TinyFishIntelligencePage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
            <Footer />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
