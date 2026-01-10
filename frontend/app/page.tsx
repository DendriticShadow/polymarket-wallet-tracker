'use client'

import { useEffect, useState } from 'react'
import { apiClient, AnalyticsSummary, Trade, Alert } from '@/lib/api'
import StatCard from '@/components/StatCard'
import Link from 'next/link'

export default function Dashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [recentTrades, setRecentTrades] = useState<Trade[]>([])
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        const [summaryData, tradesData, alertsData] = await Promise.all([
          apiClient.getAnalyticsSummary(),
          apiClient.getTrades({ limit: 5 }),
          apiClient.getAlerts({ limit: 5 }),
        ])
        setSummary(summaryData)
        setRecentTrades(tradesData)
        setRecentAlerts(alertsData)
        setError(null)
      } catch (err: any) {
        setError(err.message || 'Failed to fetch data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error && !summary) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-red-800 dark:text-red-400">Error: {error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Real-time monitoring of Polymarket trading patterns
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <StatCard
          title="Total Wallets"
          value={summary?.total_wallets.toLocaleString() || '0'}
          icon="👛"
          color="blue"
        />
        <StatCard
          title="Fresh Wallets"
          value={summary?.fresh_wallets.toLocaleString() || '0'}
          icon="🆕"
          color="green"
        />
        <StatCard
          title="Total Trades"
          value={summary?.total_trades.toLocaleString() || '0'}
          icon="💱"
          color="purple"
        />
        <StatCard
          title="Total Alerts"
          value={summary?.total_alerts.toLocaleString() || '0'}
          icon="🚨"
          color="yellow"
        />
        <StatCard
          title="Pending Alerts"
          value={summary?.pending_alerts.toLocaleString() || '0'}
          icon="⚠️"
          color="red"
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Trades */}
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-700">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Trades</h2>
            <Link
              href="/trades"
              className="text-sm text-primary hover:text-blue-700 dark:hover:text-blue-300"
            >
              View all →
            </Link>
          </div>
          <div className="p-6">
            {recentTrades.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">No trades yet</p>
            ) : (
              <div className="space-y-3">
                {recentTrades.map((trade) => (
                  <div
                    key={trade.id}
                    className="flex items-center justify-between p-3 bg-gray-50 dark:bg-slate-900 rounded-lg"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {trade.wallet_address.slice(0, 10)}...
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {trade.market_id}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        ${parseFloat(trade.token_amount).toFixed(2)}
                      </p>
                      <p className={`text-xs ${trade.trade_type === 'buy' ? 'text-green-600' : 'text-red-600'}`}>
                        {trade.trade_type.toUpperCase()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-700">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Alerts</h2>
            <Link
              href="/alerts"
              className="text-sm text-primary hover:text-blue-700 dark:hover:text-blue-300"
            >
              View all →
            </Link>
          </div>
          <div className="p-6">
            {recentAlerts.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">No alerts yet</p>
            ) : (
              <div className="space-y-3">
                {recentAlerts.map((alert) => (
                  <div
                    key={alert.id}
                    className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {alert.wallet_address.slice(0, 10)}...
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        ${parseFloat(alert.position_size).toFixed(2)} position
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-red-600 dark:text-red-400">
                        Risk: {alert.risk_score}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {alert.status}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
