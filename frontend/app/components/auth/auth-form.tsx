'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { LoginForm } from './login-form';
import { RegisterForm } from './register-form';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { initiateFacebookLogin } from '@/app/lib/auth';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2 } from 'lucide-react';

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
    <div className="relative">
      {/* Static gradient background */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-50/30 via-purple-50/30 to-pink-50/30" />
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10"
      >
        <Card className="w-[400px] mx-auto mt-20 shadow-xl border-opacity-50 backdrop-blur-md bg-white/90 hover:shadow-lg transition-shadow duration-300">
          <CardHeader className="pb-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2, duration: 0.3 }}
            >
              <CardTitle className="text-2xl font-bold text-center text-blue-600">
                Welcome Back
              </CardTitle>
            </motion.div>
          </CardHeader>
          <CardContent className="pb-6 relative">
            {/* Simple background */}
            <div className="absolute inset-0 bg-blue-50/10 rounded-xl" />
            <div className="relative">
              <Tabs defaultValue={defaultTab} className="w-full">
                <TabsList className="grid w-full grid-cols-2 p-1 mb-6 bg-gradient-to-r from-gray-100/50 to-gray-50/50 backdrop-blur-sm">
                  <TabsTrigger 
                    value="login" 
                    className="data-[state=active]:bg-blue-500 data-[state=active]:text-white transition-colors duration-200"
                  >
                    Login
                  </TabsTrigger>
                  <TabsTrigger 
                    value="register"
                    className="data-[state=active]:bg-blue-500 data-[state=active]:text-white transition-colors duration-200"
                  >
                    Register
                  </TabsTrigger>
                </TabsList>
                <AnimatePresence mode="sync">
                  <TabsContent value="login" key="login">
                    <motion.div
                      key="login-motion"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <LoginForm onSuccess={() => router.push('/dashboard')} />
                    </motion.div>
                  </TabsContent>
                  <TabsContent value="register" key="register">
                    <motion.div
                      key="register-motion"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      <RegisterForm onSuccess={() => router.push('/dashboard')} />
                    </motion.div>
                  </TabsContent>
                </AnimatePresence>
                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-200" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="bg-white px-4 text-gray-500">Or continue with</span>
                  </div>
                </div>
                <div className="relative">
                  <motion.div
                    whileHover={{ opacity: 0.9 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Button
                      variant="outline"
                      className="w-full transition-[border-color,box-shadow] duration-300 border-2 h-11 backdrop-blur-sm relative overflow-hidden group hover:shadow-md"
                      onClick={handleFacebookLogin}
                      disabled={isLoading}
                      aria-disabled={isLoading}
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-100/0 via-blue-100/30 to-blue-100/0 opacity-0 group-hover:opacity-100 transition-opacity" />
                      {isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          <span className="relative z-10">Connecting...</span>
                        </>
                      ) : (
                        <>
                          <FacebookIcon className="mr-2 h-5 w-5 text-blue-600 transition-colors duration-300" />
                          <span className="text-gray-700 relative z-10">Continue with Facebook</span>
                        </>
                      )}
                    </Button>
                  </motion.div>
                </div>
              </Tabs>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

interface FacebookIconProps extends React.SVGProps<SVGSVGElement> {}

function FacebookIcon(props: FacebookIconProps) {
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