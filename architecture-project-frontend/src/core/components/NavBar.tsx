import { Link } from 'react-router-dom'
import { Button } from '@/shared/components/ui/button'
import { useAuth } from '../auth/AuthProvider'

export default function NavBar() {
  const { userInfo, logout, isAdmin } = useAuth()

  return (
    <header className="border-b bg-background sticky top-0 z-40">
      <div className="container mx-auto max-w-4xl px-4 h-14 flex items-center justify-between">
        <Link to="/" className="font-semibold text-sm">
          My App
        </Link>
        <div className="flex items-center gap-3">
          {isAdmin && (
            <Link
              to="/admin/users"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Users
            </Link>
          )}
          <Link
            to="/profile"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            {(userInfo?.preferred_username as string) ?? 'Profile'}
          </Link>
          <Button variant="outline" size="sm" onClick={() => logout()}>
            Log out
          </Button>
        </div>
      </div>
    </header>
  )
}
