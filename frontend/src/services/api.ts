import type {
  User,
  BeneficiaryMeResponse,
  Transaction,
  EntitlementsResponse,
  Complaint,
  Discrepancy,
  AuditSummary,
  OverviewStats,
  StateAnalytics,
  Trend,
  CommodityBreakdown,
  TinyFishStatus,
  DataSource,
  ExtractionJob,
  SourceRecord,
} from '../types';

const API_BASE = '/api';

async function fetchJson<T>(url: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem('rt_token');
  const headers = new Headers(options.headers || {});
  
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
    credentials: 'include',
  });

  if (!response.ok) {
    let errorDetail = `Request failed (${response.status})`;
    try {
      const err = await response.json();
      errorDetail = err.detail || err.message || JSON.stringify(err);
    } catch {
      errorDetail = await response.text();
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  auth: {
    login: async (username: string, password: string): Promise<{ access_token: string; user: User }> => {
      const res = await fetchJson<{ access_token: string; user: User }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      });
      if (res.access_token) {
        localStorage.setItem('rt_token', res.access_token);
      }
      return res;
    },
    logout: async (): Promise<void> => {
      try {
        await fetchJson('/auth/logout', { method: 'POST' });
      } finally {
        localStorage.removeItem('rt_token');
      }
    },
    getMe: (): Promise<User> => fetchJson<User>('/auth/me'),
  },

  beneficiary: {
    getMe: (): Promise<BeneficiaryMeResponse> => fetchJson<BeneficiaryMeResponse>('/beneficiaries/me'),
    getTransactions: (limit = 50): Promise<Transaction[]> =>
      fetchJson<Transaction[]>(`/beneficiaries/me/transactions?limit=${limit}`),
    getEntitlements: (period?: string): Promise<EntitlementsResponse> =>
      fetchJson<EntitlementsResponse>(
        period ? `/beneficiaries/me/entitlements?period=${period}` : '/beneficiaries/me/entitlements'
      ),
  },

  complaints: {
    getComplaints: (): Promise<Complaint[]> => fetchJson<Complaint[]>('/complaints'),
    getComplaintById: (id: number): Promise<Complaint> => fetchJson<Complaint>(`/complaints/${id}`),
    createComplaint: (data: {
      related_shop_id: number;
      category: string;
      description: string;
      related_transaction_id?: number;
    }): Promise<Complaint> =>
      fetchJson<Complaint>('/complaints', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    addEvent: (complaintId: number, data: { event_type: string; note: string }): Promise<Complaint> =>
      fetchJson<Complaint>(`/complaints/${complaintId}/events`, {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    updateStatus: (
      complaintId: number,
      data: { status: string; note?: string; resolution_summary?: string }
    ): Promise<Complaint> =>
      fetchJson<Complaint>(`/complaints/${complaintId}/status`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
  },

  audits: {
    getSummary: (): Promise<AuditSummary> => fetchJson<AuditSummary>('/audits/summary'),
    getDiscrepancies: (filters?: {
      status?: string;
      severity?: string;
      category?: string;
      state?: string;
    }): Promise<Discrepancy[]> => {
      const params = new URLSearchParams();
      if (filters?.status) params.set('status_filter', filters.status);
      if (filters?.severity) params.set('severity', filters.severity);
      if (filters?.category) params.set('category', filters.category);
      if (filters?.state) params.set('state', filters.state);
      const query = params.toString() ? `?${params.toString()}` : '';
      return fetchJson<Discrepancy[]>(`/audits/discrepancies${query}`);
    },
    getDiscrepancyById: (id: number): Promise<Discrepancy> =>
      fetchJson<Discrepancy>(`/audits/discrepancies/${id}`),
    reviewDiscrepancy: (id: number, data: { outcome?: string; note?: string; notes?: string }): Promise<Discrepancy> => {
      const text = data.notes || data.note || '';
      return fetchJson<Discrepancy>(`/audits/discrepancies/${id}/review`, {
        method: 'POST',
        body: JSON.stringify({ notes: text, note: text }),
      });
    },
    resolveDiscrepancy: (id: number, data: { outcome: string; note?: string; notes?: string }): Promise<Discrepancy> => {
      const text = data.notes || data.note || '';
      return fetchJson<Discrepancy>(`/audits/discrepancies/${id}/resolve`, {
        method: 'POST',
        body: JSON.stringify({ outcome: data.outcome, notes: text, note: text }),
      });
    },
    triggerAuditRun: (): Promise<{ message: string; flagged_count: number }> =>
      fetchJson<{ message: string; flagged_count: number }>('/audits/run', {
        method: 'POST',
      }),
  },

  analytics: {
    getOverview: (): Promise<OverviewStats> => fetchJson<OverviewStats>('/analytics/overview'),
    getStates: (): Promise<StateAnalytics[]> => fetchJson<StateAnalytics[]>('/analytics/states'),
    getTrends: (): Promise<Trend[]> => fetchJson<Trend[]>('/analytics/trends'),
    getCommodities: (): Promise<CommodityBreakdown[]> => fetchJson<CommodityBreakdown[]>('/analytics/commodities'),
  },

  tinyfish: {
    getStatus: (): Promise<TinyFishStatus> => fetchJson<TinyFishStatus>('/tinyfish/status'),
    getSources: (): Promise<DataSource[]> => fetchJson<DataSource[]>('/tinyfish/sources'),
    createSource: (data: { name: string; source_url: string; jurisdiction: string; source_type?: string }): Promise<DataSource> =>
      fetchJson<DataSource>('/tinyfish/sources', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    getJobs: (limit = 50): Promise<ExtractionJob[]> =>
      fetchJson<ExtractionJob[]>(`/tinyfish/jobs?limit=${limit}`),
    getJobById: (id: number): Promise<ExtractionJob> =>
      fetchJson<ExtractionJob>(`/tinyfish/jobs/${id}`),
    getJobRecords: (id: number): Promise<SourceRecord[]> =>
      fetchJson<SourceRecord[]>(`/tinyfish/jobs/${id}/records`),
    triggerJob: (data: { url?: string; reporting_period?: string; mode?: string }): Promise<ExtractionJob> =>
      fetchJson<ExtractionJob>('/tinyfish/jobs', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },
};
