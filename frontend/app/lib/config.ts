export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const endpoints = {
  // Auth endpoints
  login: `${API_URL}/api/auth/login/`,
  register: `${API_URL}/api/auth/register/`,
  facebookLogin: `${API_URL}/api/auth/login/facebook/`,
  logout: `${API_URL}/api/auth/logout/`,
  refreshToken: `${API_URL}/api/auth/token/refresh/`,

  // Communications endpoints
  whatsapp: {
    send: `${API_URL}/api/communications/whatsapp/`,
    list: `${API_URL}/api/communications/whatsapp/`,
  },
  email: {
    send: `${API_URL}/api/communications/email/`,
    list: `${API_URL}/api/communications/email/`,
  },
  communications: {
    history: `${API_URL}/api/communications/history/`,
  },
} as const;