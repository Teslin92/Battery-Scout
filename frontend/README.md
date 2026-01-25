# Battery Scout Frontend

React + TypeScript frontend for Battery Scout newsletter service.

## Tech Stack

- **Vite** - Build tool and dev server
- **React 18** - UI framework
- **TypeScript** - Type safety
- **shadcn/ui** - Component library
- **Tailwind CSS** - Styling
- **React Query** - Data fetching and caching
- **React Router** - Routing

## Development

### Prerequisites

- Node.js 18+ (recommend using [nvm](https://github.com/nvm-sh/nvm))
- npm or yarn

### Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:8080`

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_PUBLISHABLE_KEY=your_supabase_key
```

Note: The frontend now uses the FastAPI backend API instead of direct Supabase calls. The Supabase environment variables are only needed if you're using Supabase for other features.

## Build

```bash
# Production build
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/     # React components
│   ├── ui/        # shadcn/ui components
│   └── ...        # Feature components
├── pages/         # Page components
├── lib/           # Utilities and API client
├── hooks/         # Custom React hooks
└── integrations/  # Third-party integrations (Supabase)
```

## API Integration

The frontend communicates with the FastAPI backend through the API client in `src/lib/api.ts`. All API calls go through this centralized client.

## Deployment

The frontend can be deployed to:
- **Vercel** (recommended)
- **Netlify**
- **Cloudflare Pages**
- Any static hosting service

Make sure to set the `VITE_API_URL` environment variable to point to your backend API.
