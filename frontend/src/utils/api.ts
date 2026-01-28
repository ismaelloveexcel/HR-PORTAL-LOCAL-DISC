export const API_BASE = '/api'

export interface FetchOptions extends RequestInit {
  token?: string
  role?: string
}

/**
 * Fetch wrapper with authentication
 * Automatically adds Authorization and X-Role headers when token/role provided
 */
export async function fetchWithAuth(
  url: string,
  options: FetchOptions = {}
): Promise<Response> {
  const { token, role, ...fetchOptions } = options
  const isFormData = fetchOptions.body instanceof FormData

  const headers: Record<string, string> = {
    // Don't set Content-Type for FormData - browser will set it with boundary
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(fetchOptions.headers as Record<string, string> || {}),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  if (role) {
    headers['X-Role'] = role
  }

  return fetch(url, { ...fetchOptions, headers })
}
