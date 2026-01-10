import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types
export interface Wallet {
  address: string
  first_seen_date: string
  last_activity_date: string | null
  total_trades: number
  total_volume: string
  lifetime_pnl: string
  is_fresh: boolean
}

export interface Market {
  market_id: string
  title: string
  category: string | null
  end_date: string | null
  resolution_date: string | null
  resolved: boolean
  outcome: string | null
  total_volume: string | null
  holder_count: number | null
}

export interface Trade {
  id: number
  tx_hash: string
  wallet_address: string
  market_id: string
  trade_type: string
  token_amount: string
  shares: string
  price: string
  timestamp: string
}

export interface Alert {
  id: number
  wallet_address: string
  market_id: string
  trade_id: number | null
  risk_score: number
  risk_factors: Record<string, number> | null
  position_size: string
  potential_payout: string | null
  market_resolution_date: string | null
  status: string
  flagged_at: string
}

export interface AnalyticsSummary {
  total_wallets: number
  fresh_wallets: number
  total_trades: number
  total_alerts: number
  pending_alerts: number
}

// API functions
export const apiClient = {
  // Analytics
  getAnalyticsSummary: async (): Promise<AnalyticsSummary> => {
    const { data } = await api.get('/analytics/summary')
    return data
  },

  // Wallets
  getWallets: async (params?: { skip?: number; limit?: number; fresh_only?: boolean }): Promise<Wallet[]> => {
    const { data } = await api.get('/wallets', { params })
    return data
  },

  getWallet: async (address: string): Promise<Wallet> => {
    const { data } = await api.get(`/wallets/${address}`)
    return data
  },

  getWalletTrades: async (address: string, params?: { skip?: number; limit?: number }): Promise<Trade[]> => {
    const { data } = await api.get(`/wallets/${address}/trades`, { params })
    return data
  },

  // Markets
  getMarkets: async (params?: { skip?: number; limit?: number; resolved?: boolean; category?: string }): Promise<Market[]> => {
    const { data } = await api.get('/markets', { params })
    return data
  },

  getMarket: async (marketId: string): Promise<Market> => {
    const { data } = await api.get(`/markets/${marketId}`)
    return data
  },

  // Trades
  getTrades: async (params?: { skip?: number; limit?: number }): Promise<Trade[]> => {
    const { data } = await api.get('/trades', { params })
    return data
  },

  getTrade: async (txHash: string): Promise<Trade> => {
    const { data } = await api.get(`/trades/${txHash}`)
    return data
  },

  // Alerts
  getAlerts: async (params?: { skip?: number; limit?: number; status?: string; min_risk_score?: number }): Promise<Alert[]> => {
    const { data } = await api.get('/alerts', { params })
    return data
  },

  getAlert: async (id: number): Promise<Alert> => {
    const { data } = await api.get(`/alerts/${id}`)
    return data
  },

  dismissAlert: async (id: number): Promise<void> => {
    await api.post(`/alerts/${id}/dismiss`)
  },
}

export default api
