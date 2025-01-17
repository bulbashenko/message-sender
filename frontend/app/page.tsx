'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AuthForm } from './components/auth/auth-form';
import { getCurrentUser } from './lib/auth';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const user = getCurrentUser();
    if (user) {
      router.push('/dashboard');
    }
  }, [router]);

  return (
    <main className="min-h-screen flex items-center justify-center p-4">
      <AuthForm />
    </main>
  );
}