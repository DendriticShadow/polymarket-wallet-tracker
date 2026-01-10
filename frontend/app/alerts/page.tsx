'use client'

import { useEffect, useState } from 'react'
import { apiClient, Alert } from '@/lib/api'
import { formatDistanceToNow } from 'date-fns'

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'pending' | 'won' | 'lost'>('all')
  const [minRisk, setMinRisk] = useState<number>(0)
  const [page, setPage] = useState(0)
  const limit = 50

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        setLoading(true)
        const params: any = { skip: page * limit, limit }
        if (filter !== 'all') params.status = filter
        if (minRisk > 0) params.min_risk_score = minRisk

        const data = await apiClient.getAlerts(params)
        setAlerts(data)
      } catch (err) {
        console.error('Failed to fetch alerts:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchAlerts()
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchAlerts, 30000)
    return () => clearInterval(interval)
  }, [filter, minRisk, page])

  const getRiskColor = (score: number) => {
    if (score >= 30) return 'text-red-600 dark:text-red-400'
    if (score >= 20) return 'text-orange-600 dark:text-orange-400'
    return 'text-yellow-600 dark:text-yellow-400'
  }

  const getRiskBg = (score: number) => {
    if (score >= 30) return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
    if (score >= 20) return 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800'
    return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Suspicious Activity Alerts</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Flagged wallets with potential insider trading patterns
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex flex-wrap gap-2">
          {['all', 'pending', 'won', 'lost'].map((status) => (
            <button
              key={status}
              onClick={() => {
                setFilter(status as any)
                setPage(0)
              }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors capitalize ${
                filter === status
                  ? 'bg-primary text-white'
                  : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700'
              }`}
            >
              {status}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2">
          <label className="text-sm text-gray-600 dark:text-gray-400">Min Risk:</label>
          <select
            value={minRisk}
            onChange={(e) => {
              setMinRisk(Number(e.target.value))
              setPage(0)
            }}
            className="px-3 py-2 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 rounded-lg text-sm text-gray-900 dark:text-white"
          >
            <option value={0}>All</option>
            <option value={20}>20+</option>
            <option value={25}>25+</option>
            <option value={30}>30+</option>
            <option value={35}>35+</option>
          </select>
        </div>
      </div>

      {/* Alerts Grid */}
      {loading && alerts.length === 0 ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : alerts.length === 0 ? (
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-700 p-12 text-center">
          <div className="text-6xl mb-4">🎉</div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No alerts found</h3>
          <p className="text-gray-500 dark:text-gray-400">
            No suspicious activity detected with the current filters
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`rounded-lg shadow-sm border p-6 ${getRiskBg(alert.risk_score)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <span className={`text-3xl font-bold ${getRiskColor(alert.risk_score)}`}>
                      {alert.risk_score}
                    </span>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Risk Score Alert
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Flagged {formatDistanceToNow(new Date(alert.flagged_at), { addSuffix: true })}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 uppercase">Wallet</p>
                      <p className="text-sm font-mono text-gray-900 dark:text-white mt-1">
                        {alert.wallet_address.slice(0, 10)}...{alert.wallet_address.slice(-6)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 uppercase">Position Size</p>
                      <p className="text-sm font-medium text-gray-900 dark:text-white mt-1">
                        ${parseFloat(alert.position_size).toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 uppercase">Potential Payout</p>
                      <p className="text-sm font-medium text-green-600 dark:text-green-400 mt-1">
                        {alert.potential_payout
                          ? `$${parseFloat(alert.potential_payout).toLocaleString()}`
                          : 'N/A'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 uppercase">Status</p>
                      <span
                        className={`inline-block mt-1 px-2 py-1 text-xs font-medium rounded-full ${
                          alert.status === 'pending'
                            ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400'
                            : alert.status === 'won'
                            ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                        }`}
                      >
                        {alert.status}
                      </span>
                    </div>
                  </div>

                  {alert.risk_factors && (
                    <div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 uppercase mb-2">
                        Risk Factors
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(alert.risk_factors).map(([factor, score]) => (
                          <span
                            key={factor}
                            className="px-2 py-1 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 rounded text-xs"
                          >
                            {factor.replace(/_/g, ' ')}: <strong>{score}</strong>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="mt-4">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Market ID</p>
                    <p className="text-xs font-mono text-gray-700 dark:text-gray-300 truncate">
                      {alert.market_id}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {alerts.length > 0 && (
        <div className="flex items-center justify-between">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <span className="text-sm text-gray-700 dark:text-gray-300">Page {page + 1}</span>
          <button
            onClick={() => setPage(page + 1)}
            disabled={alerts.length < limit}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}
