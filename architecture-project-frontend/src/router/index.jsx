import { createBrowserRouter } from 'react-router-dom'
import ProtectedRoute from '../core/components/ProtectedRoute'
import DashboardPage from '../features/items/pages/DashboardPage'
import ItemDetailPage from '../features/items/pages/ItemDetailPage'
import ProfilePage from '../features/users/pages/ProfilePage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <ProtectedRoute><DashboardPage /></ProtectedRoute>,
  },
  {
    path: '/items/:id',
    element: <ProtectedRoute><ItemDetailPage /></ProtectedRoute>,
  },
  {
    path: '/profile',
    element: <ProtectedRoute><ProfilePage /></ProtectedRoute>,
  },
])
