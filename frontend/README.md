# Polymarket Tracker Frontend

Modern React/Next.js dashboard for visualizing Polymarket trading activity and suspicious patterns.

## Features

- **Real-time Dashboard** - Live stats and recent activity
- **Wallet Tracking** - Monitor all wallets with fresh/established filtering
- **Market Browser** - Browse and filter prediction markets
- **Live Trade Feed** - Real-time stream of trading activity (auto-refresh)
- **Alerts System** - View flagged suspicious activity with risk scoring
- **Dark Mode Support** - Automatic dark/light theme
- **Responsive Design** - Works on desktop, tablet, and mobile

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Axios** - API client
- **date-fns** - Date formatting
- **Recharts** - Data visualization (ready for charts)

## Development

### Prerequisites

- Node.js 18+
- Backend API running on port 8000

### Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

The app will be available at http://localhost:3000

### Environment Variables

Create a `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── app/                 # Next.js App Router pages
│   ├── page.tsx        # Dashboard (/)
│   ├── wallets/        # Wallets page
│   ├── markets/        # Markets page
│   ├── trades/         # Trades page
│   ├── alerts/         # Alerts page
│   ├── layout.tsx      # Root layout
│   └── globals.css     # Global styles
├── components/          # Reusable components
│   ├── Navigation.tsx  # Top nav bar
│   └── StatCard.tsx    # Stat display card
├── lib/                # Utilities
│   └── api.ts          # API client & types
└── public/             # Static assets
```

## Pages

### Dashboard (/)
- Summary statistics cards
- Recent trades preview
- Recent alerts preview
- Auto-refreshes every 30 seconds

### Wallets (/wallets)
- Paginated wallet table
- Filter by fresh/all wallets
- Shows status, trades, volume, P&L
- Copy address functionality

### Markets (/markets)
- Grid view of markets
- Filter by all/active/resolved
- Category tags
- Volume and holder count

### Trades (/trades)
- Live feed of recent trades
- Auto-refreshes every 15 seconds
- Paginated table view
- Buy/sell indicators

### Alerts (/alerts)
- Flagged suspicious activity
- Filter by status and risk score
- Detailed risk factor breakdown
- Auto-refreshes every 30 seconds

## API Integration

All API calls are centralized in `lib/api.ts`:

```typescript
import { apiClient } from '@/lib/api'

// Get summary stats
const summary = await apiClient.getAnalyticsSummary()

// Get wallets
const wallets = await apiClient.getWallets({
  limit: 50,
  fresh_only: true
})

// Get alerts
const alerts = await apiClient.getAlerts({
  min_risk_score: 25,
  status: 'pending'
})
```

## Customization

### Colors

Edit `tailwind.config.js` to customize the color scheme:

```js
theme: {
  extend: {
    colors: {
      primary: '#3b82f6',    // Blue
      secondary: '#8b5cf6',  // Purple
      danger: '#ef4444',     // Red
      success: '#10b981',    // Green
      warning: '#f59e0b',    // Yellow
    },
  },
}
```

### Auto-refresh Intervals

Each page has configurable refresh intervals:

- Dashboard: 30s
- Trades: 15s
- Alerts: 30s

Edit the `setInterval` duration in each page component.

## Docker Deployment

The frontend is included in the main `docker-compose.yml`:

```bash
# Start all services including frontend
docker-compose up -d

# View frontend logs
docker-compose logs -f frontend

# Rebuild frontend only
docker-compose up -d --build frontend
```

Frontend will be available at http://localhost:3000

## Performance

- Static generation where possible
- Client-side data fetching with caching
- Pagination for large datasets
- Optimized bundle size with Next.js
- Code splitting per page

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome)
