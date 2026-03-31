import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'
import { clearAuthTokens, getAccessToken, setAccessTokenOnly } from '../auth/tokenStorage'

export function SettingsPage() {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [token, setToken] = useState(getAccessToken() ?? '')
  const [status, setStatus] = useState<string>('')

  const saveToken = () => {
    const cleaned = token.trim()

    if (!cleaned) {
      setStatus('Token is empty')
      return
    }

    setAccessTokenOnly(cleaned)
    setToken(cleaned)
    setStatus('Access token saved (refresh token is not set)')
  }

  const handleLogout = () => {
    clearAuthTokens()
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <div className="max-w-2xl rounded-xl border border-slate-200 bg-white p-4">
      <h2 className="text-lg font-semibold text-slate-900">Auth settings</h2>
      <p className="mt-2 text-sm text-slate-600">JWT stub for API requests.</p>
      <textarea
        className="mt-3 min-h-28 w-full rounded-lg border border-slate-300 p-2 text-sm"
        value={token}
        onChange={(event) => setToken(event.target.value)}
        placeholder="Paste JWT token"
      />
      <button
        type="button"
        className="mt-3 rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white"
        onClick={saveToken}
      >
        Save token
      </button>
      <button
        type="button"
        className="mt-3 ml-2 rounded-lg bg-rose-600 px-3 py-2 text-sm font-medium text-white"
        onClick={handleLogout}
      >
        Logout
      </button>
      {status && <p className="mt-2 text-sm text-slate-600">{status}</p>}
    </div>
  )
}
