import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import MembershipsPage from './pages/MembershipsPage'
import TrainersPage from './pages/TrainersPage'
import SchedulePage from './pages/SchedulePage'
import PromotionsPage from './pages/PromotionsPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'
import TrainerDetailPage from './pages/TrainerDetailPage'
import StatisticsPage from './pages/StatisticsPage'
import AdminLayout from './pages/admin/AdminLayout'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminMemberships from './pages/admin/AdminMemberships'
import AdminTrainers from './pages/admin/AdminTrainers'
import AdminServices from './pages/admin/AdminServices'
import AdminSchedule from './pages/admin/AdminSchedule'
import AdminPromotions from './pages/admin/AdminPromotions'
import AdminUsers from './pages/admin/AdminUsers'
import AdminAnalytics from './pages/admin/AdminAnalytics'
import { useLocation } from 'react-router-dom'

function Layout({ children }) {
  const { pathname } = useLocation()
  const isAdmin = pathname.startsWith('/admin')
  const isAuth = pathname === '/login' || pathname === '/register'

  return (
    <div className="app">
      {!isAdmin && <Navbar />}
      <main className="main-content">{children}</main>
      {!isAdmin && (
        <footer className="footer">
          <div className="footer-inner">
            <span>© 2026 FitClub — Все права защищены</span>
            <span>г. Алматы, ул. Спортивная, 1</span>
          </div>
        </footer>
      )}
      {/* Кнопка печати — показывается на всех страницах кроме auth и admin */}
      {!isAdmin && !isAuth && (
        <button
          className="print-btn"
          onClick={() => window.print()}
          title="Распечатать страницу"
          aria-label="Распечатать текущую страницу"
        >
          🖨️ Печать
        </button>
      )}
    </div>
  )
}

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/memberships" element={<MembershipsPage />} />
        <Route path="/trainers" element={<TrainersPage />} />
        <Route path="/schedule" element={<SchedulePage />} />
        <Route path="/promotions" element={<PromotionsPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/trainers/:id" element={<TrainerDetailPage />} />
        <Route path="/statistics" element={<StatisticsPage />} />
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<AdminDashboard />} />
          <Route path="memberships" element={<AdminMemberships />} />
          <Route path="trainers" element={<AdminTrainers />} />
          <Route path="services" element={<AdminServices />} />
          <Route path="schedule" element={<AdminSchedule />} />
          <Route path="promotions" element={<AdminPromotions />} />
          <Route path="users" element={<AdminUsers />} />
          <Route path="analytics" element={<AdminAnalytics />} />
        </Route>
      </Routes>
    </Layout>
  )
}
