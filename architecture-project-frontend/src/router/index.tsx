import { createBrowserRouter, Outlet } from 'react-router-dom'
import ProtectedRoute from '../core/components/ProtectedRoute'
import AdminRoute from '../core/components/AdminRoute'
import NavBar from '../core/components/NavBar'
import DashboardPage from '../features/items/pages/DashboardPage'
import ItemDetailPage from '../features/items/pages/ItemDetailPage'
import ProfilePage from '../features/users/pages/ProfilePage'
import AdminUsersPage from '../features/users/pages/AdminUsersPage'
import ShowcasePage from '../features/showcase/pages/ShowcasePage'

function AppLayout() {
  return (
    <>
      <NavBar />
      <Outlet />
    </>
  )
}

export const router = createBrowserRouter([
  {
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    children: [
      { path: '/', element: <DashboardPage /> },
      { path: '/items/:id', element: <ItemDetailPage /> },
      { path: '/profile', element: <ProfilePage /> },
      { path: '/showcase', element: <ShowcasePage /> },
      {
        path: '/admin/users',
        element: (
          <AdminRoute>
            <AdminUsersPage />
          </AdminRoute>
        ),
      },
    ],
  },
])

//Outlet is where the children are loaded along with the navbar
//The Protected Route is where authentication is guarded
