'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LoginForm } from './login-form';
import { RegisterForm } from './register-form';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { initiateFacebookLogin } from '@/app/lib/auth';


interface AuthFormProps {
  defaultTab?: 'login' | 'register';
}

export function AuthForm({ defaultTab = 'login' }: AuthFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleFacebookLogin = () => {
    setIsLoading(true);
    initiateFacebookLogin();
  };

  return (
    <Card className="w-[400px] mx-auto mt-20">
      <CardHeader>
        <CardTitle className="text-center">Welcome</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue={defaultTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Login</TabsTrigger>
            <TabsTrigger value="register">Register</TabsTrigger>
          </TabsList>
          <TabsContent value="login">
            <LoginForm onSuccess={() => router.push('/dashboard')} />
          </TabsContent>
          <TabsContent value="register">
            <RegisterForm onSuccess={() => router.push('/dashboard')} />
          </TabsContent>
          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-white px-2 text-gray-500">Or continue with</span>
            </div>
          </div>
          <Button
            variant="outline"
            className="w-full"
            onClick={handleFacebookLogin}
            disabled={isLoading}
            aria-disabled={isLoading}
          >
            <FacebookIcon className="mr-2 h-4 w-4" />
            {isLoading ? 'Connecting...' : 'Continue with Facebook'}
          </Button>
        </Tabs>
      </CardContent>
    </Card>
  );
}

function FacebookIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z" />
    </svg>
  );
}