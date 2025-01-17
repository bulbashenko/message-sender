'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AuthForm } from './components/auth/auth-form';
import { getCurrentUser } from './lib/auth';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const user = await getCurrentUser();
        if (user) {
          router.push('/dashboard');
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        // If auth check fails, stay on the login page
      }
    };
    
    checkAuth();
  }, [router]);

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <AuthForm />
    </main>
  );
}