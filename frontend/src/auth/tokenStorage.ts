const ACCESS_KEY = 'carb_access_token'
const REFRESH_KEY = 'carb_refresh_token'
const LEGACY_KEY = 'carb_jwt'
const AUTH_EVENT = 'carb-auth-changed'

function notifyAuthChanged() {
  window.dispatchEvent(new Event(AUTH_EVENT))
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_KEY) ?? localStorage.getItem(LEGACY_KEY)
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY)
}

export function setAuthTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem(ACCESS_KEY, accessToken)
  localStorage.setItem(REFRESH_KEY, refreshToken)
  localStorage.setItem(LEGACY_KEY, accessToken)
  notifyAuthChanged()
}

export function setAccessTokenOnly(accessToken: string) {
  localStorage.setItem(ACCESS_KEY, accessToken)
  localStorage.setItem(LEGACY_KEY, accessToken)
  notifyAuthChanged()
}

export function clearAuthTokens() {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
  localStorage.removeItem(LEGACY_KEY)
  notifyAuthChanged()
}

export const AUTH_CHANGED_EVENT = AUTH_EVENT
