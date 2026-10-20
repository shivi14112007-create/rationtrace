import React, { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

export type Language = 'en' | 'hi';

interface Translations {
  [key: string]: {
    en: string;
    hi: string;
  };
}

export const translations: Translations = {
  // Navigation & Brand
  app_name: { en: 'RationTrace', hi: 'राशनट्रेस' },
  app_tagline: { en: 'Public Distribution Intelligence & Audit Platform', hi: 'सार्वजनिक वितरण आसूचना एवं ऑडिट मंच' },
  nav_home: { en: 'Overview', hi: 'मुखपृष्ठ' },
  nav_analytics: { en: 'State Intelligence', hi: 'राज्य विश्लेषण' },
  nav_beneficiary: { en: 'Beneficiary Portal', hi: 'लाभार्थी पोर्टल' },
  nav_audits: { en: 'Official Audits', hi: 'अधिकारिक ऑडिट' },
  nav_tinyfish: { en: 'TinyFish Center', hi: 'टाइनीफिश केंद्र' },
  nav_login: { en: 'Sign In', hi: 'लॉग इन' },
  nav_logout: { en: 'Sign Out', hi: 'लॉग आउट' },
  live_data: { en: 'Live Data Mode', hi: 'लाइव डेटा मोड' },
  demo_data: { en: 'Demo Dataset', hi: 'डेमो डेटासेट' },
  demo_notice: {
    en: 'RationTrace is running in transparent demonstration mode with verified public datasets.',
    hi: 'राशनट्रेस पारदर्शी डेमो मोड में सत्यापित सार्वजनिक डेटासेट के साथ संचालित है।',
  },

  // Hero & Landing
  hero_title: { en: 'Every Entitlement Deserves Transparency', hi: 'हर राशन हक में पारदर्शिता' },
  hero_subtitle: {
    en: 'Real-time reconciliation of public food grain allocations, cross-portal web intelligence, and evidence-backed grievance redressal for India’s Public Distribution System.',
    hi: 'राष्ट्रीय सार्वजनिक वितरण प्रणाली में खाद्यान्न आवंटन का वास्तविक समय समाधान, वेब आसूचना एवं साक्ष्य-आधारित शिकायत निवारण।',
  },
  explore_dashboard: { en: 'Explore State Analytics', hi: 'राज्य विश्लेषण देखें' },
  view_beneficiary_records: { en: 'Beneficiary Access', hi: 'लाभार्थी रिकॉर्ड' },
  official_portal: { en: 'Official Audit Queue', hi: 'ऑडिट कतार' },
  how_it_works: { en: 'How RationTrace Works', hi: 'राशनट्रेस कैसे काम करता है' },
  step1_title: { en: '1. Web Agent Ingestion', hi: '१. वेब एजेंट डेटा संकलन' },
  step1_desc: {
    en: 'TinyFish AI navigates approved public portals (NFSA, state e-PDS) to extract authentic allocation schedules without private backdoor access.',
    hi: 'टाइनीफिश एआई बिना किसी गुप्त पिछले रास्ते के आधिकारिक पोर्टल्स से प्रमाणित आवंटन डेटा निष्कर्षित करता है।',
  },
  step2_title: { en: '2. Transparent Audit Engine', hi: '२. पारदर्शी ऑडिट इंजन' },
  step2_desc: {
    en: 'Mathematical balancing rules (Opening + Received - Distributed = Closing) detect unaccounted shortfalls or negative stock automatically.',
    hi: 'गणितीय समीकरण (प्रारंभिक + प्राप्त - वितरित = अंतिम स्टॉक) बिना किसी पूर्वाग्रह के विसंगतियों का तुरंत पता लगाते हैं।',
  },
  step3_title: { en: '3. Evidence-Backed Grievance', hi: '३. साक्ष्य-समर्थित शिकायत निवारण' },
  step3_desc: {
    en: 'Citizens compare verified entitlement with recorded transactions and track investigations with an unalterable reference timeline.',
    hi: 'नागरिक अपने आधिकारिक हक की तुलना दर्ज लेन-देन से कर सकते हैं और शिकायत की स्थिति ट्रैक कर सकते हैं।',
  },

  // Beneficiary Page
  beneficiary_portal_title: { en: 'Citizen Ration Entitlement & Transaction Ledger', hi: 'नागरिक राशन हक एवं लेन-देन खाता' },
  masked_id: { en: 'Beneficiary ID', hi: 'लाभार्थी पहचान' },
  card_type: { en: 'Ration Card Category', hi: 'राशन कार्ड श्रेणी' },
  family_members_count: { en: 'Registered Family Members', hi: 'पंजीकृत परिवार के सदस्य' },
  assigned_fps: { en: 'Assigned Fair Price Shop', hi: 'संबद्ध राशन दुकान' },
  entitlements_heading: { en: 'Monthly Authorized Entitlement Comparison', hi: 'मासिक अधिकृत हक तुलना' },
  transactions_heading: { en: 'Recorded Distribution Transactions', hi: 'दर्ज वितरण लेन-देन' },
  commodity: { en: 'Commodity', hi: 'खाद्य सामग्री' },
  entitled_qty: { en: 'Entitled Qty', hi: 'अधिकृत मात्रा' },
  recorded_qty: { en: 'Recorded Qty', hi: 'वितरित मात्रा' },
  variance: { en: 'Discrepancy', hi: 'अंतर' },
  status: { en: 'Status', hi: 'स्थिति' },
  date: { en: 'Date', hi: 'दिनांक' },
  unit: { en: 'Unit', hi: 'इकाई' },
  report_discrepancy: { en: 'Report a Discrepancy', hi: 'विसंगति की शिकायत दर्ज करें' },
  track_complaints: { en: 'Active Grievance Trackers', hi: 'सक्रिय शिकायत ट्रैकर' },

  // Complaint Form
  file_complaint: { en: 'File a Ration Discrepancy Grievance', hi: 'राशन विसंगति की शिकायत दर्ज करें' },
  complaint_category: { en: 'Grievance Category', hi: 'शिकायत की श्रेणी' },
  category_under: { en: 'Shortage / Under-Distribution', hi: 'कम मात्रा में वितरण / कटौती' },
  category_non: { en: 'Non-Issuance of Entitlement', hi: 'अनाज का न मिलना' },
  category_overcharge: { en: 'Overcharging Above Government Rate', hi: 'सरकारी दर से अधिक वसूली' },
  category_quality: { en: 'Substandard Foodgrain Quality', hi: 'अनाज की निम्न गुणवत्ता' },
  category_shop_closed: { en: 'FPS Shop Repeatedly Closed', hi: 'दुकान का बार-बार बंद रहना' },
  description: { en: 'Detailed Description & Timeline', hi: 'विस्तृत विवरण एवं घटनाक्रम' },
  submit_complaint: { en: 'Submit to Audit Workflow', hi: 'शिकायत दर्ज करें' },
  cancel: { en: 'Cancel', hi: 'रद्द करें' },

  // Audit Page
  audit_dashboard_title: { en: 'Official PDS Audit & Case Reconciliation Queue', hi: 'अधिकारिक पीडीएस ऑडिट एवं मामला समाधान' },
  total_records: { en: 'Ingested Stock Records', hi: 'कुल स्टॉक रिकॉर्ड' },
  open_discrepancies: { en: 'Open Discrepancies', hi: 'सक्रिय विसंगतियां' },
  critical_alerts: { en: 'Critical Alerts', hi: 'गंभीर चेतावनियां' },
  rule_a_title: { en: 'Rule A: Stock Reconciliation Violations', hi: 'नियम अ: स्टॉक मिलान विसंगति' },
  rule_b_title: { en: 'Rule B: Negative Balance Detected', hi: 'नियम ब: ऋणात्मक स्टॉक का पता चलना' },
  filter_severity: { en: 'Filter Severity', hi: 'गंभीरता फ़िल्टर' },
  all_severities: { en: 'All Severities', hi: 'सभी स्तर' },
  shop_col: { en: 'Shop Identifier', hi: 'दुकान संख्या' },
  difference_col: { en: 'Calculated Variance', hi: 'गणना किया गया अंतर' },
  rule_col: { en: 'Triggered Rule', hi: 'सक्रिय नियम' },
  actions_col: { en: 'Audit Actions', hi: 'कार्रवाई' },
  inspect_case: { en: 'Inspect Evidence', hi: 'साक्ष्य देखें' },
  resolve_case: { en: 'Resolve Case', hi: 'मामला सुलझाएं' },
  case_resolved: { en: 'Resolved', hi: 'सुलझाया गया' },

  // State Analytics
  state_analytics_title: { en: 'State-Level Public Distribution Intelligence', hi: 'राज्य-स्तरीय सार्वजनिक वितरण आसूचना' },
  total_allocated: { en: 'Total State Allocation', hi: 'कुल राज्य आवंटन' },
  total_distributed: { en: 'Total Verified Distribution', hi: 'कुल सत्यापित वितरण' },
  reconciliation_rate: { en: 'System Reconciliation Rate', hi: 'प्रणाली समाधान दर' },
  active_shops: { en: 'Active Fair Price Shops', hi: 'सक्रिय राशन केंद्र' },
  allocation_chart: { en: 'State-wise Grain Allocation vs Distribution (MT)', hi: 'राज्यवार खाद्यान्न आवंटन बनाम वितरण (मीट्रिक टन)' },
  trends_chart: { en: 'Monthly Allocation & Distribution Trends', hi: 'मासिक आवंटन एवं वितरण प्रवृत्ति' },
  commodity_chart: { en: 'Commodity Share & Variance Analysis', hi: 'खाद्य सामग्री हिस्सा एवं अंतर विश्लेषण' },
  toggle_table: { en: 'Switch to Accessible Table', hi: 'तालिका रूप में देखें' },
  toggle_chart: { en: 'Switch to Graphical Chart', hi: 'चार्ट रूप में देखें' },
  data_provenance: { en: 'Data Provenance & Verification Source', hi: 'डेटा स्रोत एवं सत्यापन संदर्भ' },

  // TinyFish Page
  tinyfish_title: { en: 'TinyFish Web Agent Intelligence Center', hi: 'टाइनीफिश वेब एजेंट आसूचना केंद्र' },
  tinyfish_desc: {
    en: 'Real documented integration with TinyFish Web Agent API (POST /v1/automation/run & /run-async). Autonomous extraction from administrator-approved public food security portals.',
    hi: 'टाइनीफिश वेब एजेंट एपीआई के साथ वास्तविक प्रलेखित एकीकरण। अधिकृत खाद्य सुरक्षा पोर्टलों से स्वायत्त डेटा निष्कर्षण।',
  },
  trigger_extraction: { en: 'Trigger Agent Extraction', hi: 'एजेंट निष्कर्षण प्रारंभ करें' },
  agent_status: { en: 'Agent Engine Status', hi: 'एजेंट इंजन स्थिति' },
  approved_sources: { en: 'Admin-Approved Portals Allowlist', hi: 'प्रशासन-अनुमोदित पोर्टल सूची' },
  extraction_history: { en: 'Extraction Jobs & Run History', hi: 'निष्कर्षण कार्य एवं रन इतिहास' },
  job_id: { en: 'Job ID', hi: 'कार्य आईडी' },
  records_count: { en: 'Records Extracted', hi: 'निष्कर्षित रिकॉर्ड' },
  view_records: { en: 'Inspect Records & SHA256 Hashes', hi: 'रिकॉर्ड व हैश देखें' },

  // Login Page
  login_title: { en: 'Sign in to RationTrace', hi: 'राशनट्रेस में साइन इन करें' },
  username: { en: 'Username', hi: 'उपयोगकर्ता नाम' },
  password: { en: 'Password', hi: 'पासवर्ड' },
  demo_accounts: { en: '1-Click Role Login (Demo Identities)', hi: 'एक क्लिक में भूमिका चयन (डेमो खाते)' },
  role_beneficiary: { en: 'Beneficiary (Citizen)', hi: 'लाभार्थी (नागरिक)' },
  role_official: { en: 'Inspector (Government)', hi: 'निरीक्षक (सरकारी अधिकारी)' },
  role_dealer: { en: 'FPS Dealer (Shop Owner)', hi: 'राशन डीलर (दुकान संचालक)' },
  role_admin: { en: 'System Administrator', hi: 'सिस्टम प्रशासक' },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('rt_lang') as Language;
    return saved === 'hi' ? 'hi' : 'en';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('rt_lang', lang);
  };

  const t = (key: string): string => {
    const entry = translations[key];
    if (!entry) return key;
    return entry[language] || entry.en || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = (): LanguageContextType => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};
