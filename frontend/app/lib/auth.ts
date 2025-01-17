import { jwtDecode } from 'jwt-decode';
import Cookies from 'js-cookie';
import { endpoints, API_URL } from './config';

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
}

const AUTH_COOKIE_NAME = 'auth_tokens';
const COOKIE_EXPIRY_DAYS = 3;

export const setAuthTokens = (tokens: AuthTokens) => {
  Cookies.set(AUTH_COOKIE_NAME, JSON.stringify(tokens), { expires: COOKIE_EXPIRY_DAYS });
};

export const getAuthTokens = (): AuthTokens | null => {
  const tokens = Cookies.get(AUTH_COOKIE_NAME);
  return tokens ? JSON.parse(tokens) : null;
};

export const removeAuthTokens = () => {
  Cookies.remove(AUTH_COOKIE_NAME);
};

export const refreshTokens = async (): Promise<AuthTokens> => {
  const tokens = getAuthTokens();
  if (!tokens?.refresh) {
    removeAuthTokens();
    throw new Error('No refresh token available');
  }

  try {
    const response = await fetch(endpoints.refreshToken, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: tokens.refresh }),
    });

    const data = await response.json();
    
    // Handle both DRF and our custom response formats
    if (response.ok && (data.success || data.access)) {
      const newTokens = {
        refresh: tokens.refresh, // Keep existing refresh token
        access: data.access || data.data.access,
      };
      setAuthTokens(newTokens);
      return newTokens;
    }

    throw new Error(data.error || data.detail || 'Failed to refresh token');
  } catch (error) {
    removeAuthTokens();
    throw error;
  }
};

export const getCurrentUser = (): User | null => {
  const tokens = getAuthTokens();
  if (!tokens?.access) return null;
  
  try {
    const decoded = jwtDecode<User>(tokens.access);
    // Check if token is expired
    if ((decoded as any).exp * 1000 < Date.now()) {
      return null;
    }
    return decoded;
  } catch {
    return null;
  }
};

export const getAuthHeaders = async (): Promise<Record<string, string>> => {
  let tokens = getAuthTokens();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };

  try {
    if (tokens?.access) {
      // Check if token is expired
      const decoded = jwtDecode<{ exp: number }>(tokens.access);
      const isExpired = decoded.exp * 1000 < Date.now();

      // If token is expired, try to refresh
      if (isExpired) {
        tokens = await refreshTokens();
      }

      headers['Authorization'] = `Bearer ${tokens.access}`;
    }

    return headers;
  } catch (error) {
    console.error('Token validation error:', error);
    removeAuthTokens();
    throw new Error('Authentication required');
  }
};

export const login = async (email: string, password: string) => {
  const response = await fetch(endpoints.login, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) throw new Error('Login failed');
  
  const data = await response.json();
  if (!data.success) throw new Error(data.error || 'Login failed');
  
  setAuthTokens(data.data);
  return data.data;
};

export const register = async (email: string, password: string) => {
  try {
    const response = await fetch(endpoints.register, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.toLowerCase(), password }),
    });

    const data = await response.json();
    
    // Always check data.success as the backend always returns a structured response
    if (!data.success) {
      throw new Error(data.error);
    }
    
    setAuthTokens(data.data);
    return data.data;
  } catch (error: any) {
    // If it's our error with a message, use it
    if (error.message) {
      throw error;
    }
    // For network or other errors
    throw new Error('Registration failed. Please try again.');
  }
};



export const logout = async () => {
  try {
    const tokens = getAuthTokens();
    if (!tokens?.refresh) {
      removeAuthTokens();
      return;
    }

    try {
      const headers = await getAuthHeaders();
      const response = await fetch(endpoints.logout, {
        method: 'POST',
        headers,
        body: JSON.stringify({ refresh: tokens.refresh }),
      });

      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Logout failed');
      }
    } catch (error) {
      // If token refresh fails during logout, just remove tokens
      console.error('Logout error:', error);
    }
  } finally {
    removeAuthTokens();
  }
};

export const initiateFacebookLogin = () => {
  const FACEBOOK_APP_ID = process.env.NEXT_PUBLIC_FACEBOOK_APP_ID;
  const REDIRECT_URI = `${window.location.origin}/auth/facebook/callback`;
  const state = Math.random().toString(36).substring(7);
  
  // Store state for validation
  sessionStorage.setItem('fbAuthState', state);
  
  const fbLoginUrl = `https://www.facebook.com/v12.0/dialog/oauth?` +
    `client_id=${FACEBOOK_APP_ID}&` +
    `redirect_uri=${encodeURIComponent(REDIRECT_URI)}&` +
    `state=${state}&` +
    `response_type=code&` +
    `scope=email,public_profile`;
  
  window.location.href = fbLoginUrl;
};

export const handleFacebookCallback = async (code: string) => {
  try {
    const REDIRECT_URI = `${window.location.origin}/auth/facebook/callback`;

    // Send the authorization code directly to our backend
    const response = await fetch(endpoints.facebookLogin, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        code,
        redirect_uri: REDIRECT_URI
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Facebook login failed');
    }
    
    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Facebook login failed');
    }
    
    setAuthTokens(data.data);
    return data.data;
  } catch (error) {
    console.error('Facebook authentication error:', error);
    throw error;
  }
};