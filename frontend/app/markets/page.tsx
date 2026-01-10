'use client'

import { useEffect, useState } from 'react'
import { apiClient, Market } from '@/lib/api'
import { formatDistanceToNow } from 'date-fns'

export default function MarketsPage() {
  const [markets, setMarkets] = useState<Market[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'active' | 'resolved'>('all')
  const [page, setPage] = useState(0)
  const limit = 50

  useEffect(() => {
    const fetchMarkets = async () => {
      try {
        setLoading(true)
        const params: any = { skip: page * limit, limit }
        if (filter === 'active') params.resolved = false
        if (filter === 'resolved') params.resolved = true

        const data = await apiClient.getMarkets(params)
        setMarkets(data)
      } catch (err) {
        console.error('Failed to fetch markets:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchMarkets()
  }, [filter, page])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Markets</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Browse and monitor prediction markets
        </p>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => {
            setFilter('all')
            setPage(0)
          }}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'all'
              ? 'bg-primary text-white'
              : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700'
          }`}
        >
          All Markets
        </button>
        <button
          onClick={() => {
            setFilter('active')
            setPage(0)
          }}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'active'
              ? 'bg-primary text-white'
              : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700'
          }`}
        >
          Active
        </button>
        <button
          onClick={() => {
            setFilter('resolved')
            setPage(0)
          }}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            filter === 'resolved'
              ? 'bg-primary text-white'
              : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700'
          }`}
        >
          Resolved
        </button>
      </div>

      {/* Markets Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-full flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : markets.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <p className="text-gray-500 dark:text-gray-400">No markets found</p>
          </div>
        ) : (
          markets.map((market) => (
            <div
              key={market.market_id}
              className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-700 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                {market.category && (
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400">
                    {market.category}
                  </span>
                )}
                {market.resolved ? (
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400">
                    Resolved
                  </span>
                ) : (
                  <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-400">
                    Active
                  </span>
                )}
              </div>

              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
                {market.title}
              </h3>

              <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                {market.total_volume && (
                  <div className="flex justify-between">
                    <span>Volume:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      ${parseFloat(market.total_volume).toLocaleString()}
                    </span>
                  </div>
                )}
                {market.holder_count && (
                  <div className="flex justify-between">
                    <span>Holders:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {market.holder_count}
                    </span>
                  </div>
                )}
                {market.outcome && (
                  <div className="flex justify-between">
                    <span>Outcome:</span>
                    <span className="font-medium text-gray-900 dark:text-white">
                      {market.outcome}
                    </span>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-slate-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 font-mono truncate">
                  {market.market_id}
                </p>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setPage(Math.max(0, page - 1))}
          disabled={page === 0}
          className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Previous
        </button>
        <span className="text-sm text-gray-700 dark:text-gray-300">
          Page {page + 1}
        </span>
        <button
          onClick={() => setPage(page + 1)}
          disabled={markets.length < limit}
          className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-700 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Next
        </button>
      </div>
    </div>
  )
}
