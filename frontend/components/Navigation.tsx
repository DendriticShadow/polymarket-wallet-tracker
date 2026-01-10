'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import clsx from 'clsx'

const Navigation = () => {
  const pathname = usePathname()

  const links = [
    { href: '/', label: 'Dashboard', icon: '📊' },
    { href: '/wallets', label: 'Wallets', icon: '👛' },
    { href: '/markets', label: 'Markets', icon: '📈' },
    { href: '/trades', label: 'Trades', icon: '💱' },
    { href: '/alerts', label: 'Alerts', icon: '🚨' },
  ]

  return (
    <nav className="bg-white dark:bg-slate-800 shadow-sm border-b border-gray-200 dark:border-slate-700">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link href="/" className="flex items-center space-x-2">
              <span className="text-2xl">🔍</span>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                Polymarket Tracker
              </span>
            </Link>

            <div className="hidden md:flex space-x-1">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={clsx(
                    'px-3 py-2 rounded-md text-sm font-medium transition-colors',
                    pathname === link.href
                      ? 'bg-primary text-white'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                  )}
                >
                  <span className="mr-1">{link.icon}</span>
                  {link.label}
                </Link>
              ))}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500 dark:text-gray-400">
              v0.1.0
            </span>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navigation
