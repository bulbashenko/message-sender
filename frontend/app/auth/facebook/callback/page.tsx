'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { handleFacebookCallback } from '@/app/lib/auth';

export default function FacebookCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get('code');
    const error = searchParams.get('error');
    const state = searchParams.get('state');
    const storedState = sessionStorage.getItem('fbAuthState');
    
    // Clear stored state
    sessionStorage.removeItem('fbAuthState');

    if (error) {
      console.error('Facebook OAuth error:', error);
      setError(error);
      setTimeout(() => router.push('/'), 3000);
      return;
    }

    if (!code) {
      setError('No authorization code provided');
      setTimeout(() => router.push('/'), 3000);
      return;
    }

    if (!state || !storedState || state !== storedState) {
      console.error('Invalid state parameter');
      setError('Authentication failed - Invalid state');
      setTimeout(() => router.push('/'), 3000);
      return;
    }

    const handleCallback = async () => {
      try {
        await handleFacebookCallback(code);
        router.push('/dashboard');
      } catch (error) {
        console.error('Facebook authentication failed:', error);
        setError('Authentication failed');
        setTimeout(() => router.push('/'), 3000);
      }
    };

    handleCallback();
  }, [router, searchParams]);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h1 className="text-2xl font-semibold mb-4 text-red-600">Authentication Failed</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <p className="text-gray-500">Redirecting you back...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h1 className="text-2xl font-semibold mb-4">Completing login...</h1>
        <p className="text-gray-600">Please wait while we authenticate you.</p>
      </div>
    </div>
  );
}