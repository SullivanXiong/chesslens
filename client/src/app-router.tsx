import { createBrowserRouter, RouterProvider, Outlet, NavLink } from 'react-router-dom';
import { Home, BarChart3, Swords, BookOpen, AlertTriangle, User, MessageSquare, ChevronRight } from 'lucide-react';

// Lazy imports for pages
import { lazy, Suspense } from 'react';
const HomePage = lazy(() => import('@/pages/home-page'));
const DashboardPage = lazy(() => import('@/pages/dashboard-page'));
const GamesPage = lazy(() => import('@/pages/games-page'));
const GameDetailPage = lazy(() => import('@/pages/game-detail-page'));
const OpeningsPage = lazy(() => import('@/pages/openings-page'));
const WeaknessesPage = lazy(() => import('@/pages/weaknesses-page'));
const PlaystylePage = lazy(() => import('@/pages/playstyle-page'));
const ChatPage = lazy(() => import('@/pages/chat-page'));

function Layout() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b px-6 py-3 flex items-center gap-4">
        <NavLink to="/" className="text-xl font-bold">ChessLens</NavLink>
      </header>
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Suspense fallback={<div className="flex items-center justify-center h-64">Loading...</div>}>
          <Outlet />
        </Suspense>
      </main>
    </div>
  );
}

function PlayerLayout() {
  return (
    <div className="flex gap-6">
      <nav className="w-48 shrink-0 space-y-1">
        <SideLink to="" icon={BarChart3} label="Dashboard" end />
        <SideLink to="games" icon={Swords} label="Games" />
        <SideLink to="openings" icon={BookOpen} label="Openings" />
        <SideLink to="weaknesses" icon={AlertTriangle} label="Weaknesses" />
        <SideLink to="playstyle" icon={User} label="Playstyle" />
        <SideLink to="chat" icon={MessageSquare} label="Coach" />
      </nav>
      <div className="flex-1 min-w-0">
        <Suspense fallback={<div className="flex items-center justify-center h-64">Loading...</div>}>
          <Outlet />
        </Suspense>
      </div>
    </div>
  );
}

function SideLink({ to, icon: Icon, label, end }: { to: string; icon: any; label: string; end?: boolean }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        `flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors ${isActive ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:bg-muted'}`
      }
    >
      <Icon className="h-4 w-4" />
      {label}
    </NavLink>
  );
}

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { index: true, element: <HomePage /> },
      {
        path: ':username',
        element: <PlayerLayout />,
        children: [
          { index: true, element: <DashboardPage /> },
          { path: 'games', element: <GamesPage /> },
          { path: 'games/:gameId', element: <GameDetailPage /> },
          { path: 'openings', element: <OpeningsPage /> },
          { path: 'weaknesses', element: <WeaknessesPage /> },
          { path: 'playstyle', element: <PlaystylePage /> },
          { path: 'chat', element: <ChatPage /> },
        ],
      },
    ],
  },
]);

export default function AppRouter() {
  return <RouterProvider router={router} />;
}
