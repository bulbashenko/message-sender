'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Loader2, Eye, EyeOff } from 'lucide-react';
import { login } from '@/app/lib/auth';
import { motion } from 'framer-motion';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

interface LoginFormProps {
  onSuccess: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (values: LoginFormValues) => {
    try {
      setIsLoading(true);
      await login(values.email, values.password);
      onSuccess();
    } catch (error) {
      console.error('Login failed:', error);
      form.setError('root', {
        message: 'Invalid email or password',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem className="relative">
                <FormLabel 
                  className={cn(
                    "absolute left-3 transition-all duration-200 pointer-events-none",
                    field.value ? "-top-2.5 text-xs bg-white px-1 text-blue-500" : "top-3.5 text-gray-500"
                  )}
                >
                  Email
                </FormLabel>
                <FormControl>
                  <Input 
                    placeholder="" 
                    className="h-11 transition-[border-color,box-shadow] duration-200 border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-300 pl-3 pt-4"
                    autoComplete="username"
                    {...field} 
                  />
                </FormControl>
                <motion.div
                  initial={false}
                  animate={form.formState.errors.email ? { opacity: 1, y: 0 } : { opacity: 0, y: -10 }}
                >
                  <FormMessage className="text-xs" />
                </motion.div>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem className="relative">
                <FormLabel 
                  className={cn(
                    "absolute left-3 transition-all duration-200 pointer-events-none",
                    field.value ? "-top-2.5 text-xs bg-white px-1 text-blue-500" : "top-3.5 text-gray-500"
                  )}
                >
                  Password
                </FormLabel>
                <FormControl>
                  <div className="relative group">
                    <Input
                      type={showPassword ? "text" : "password"}
                      placeholder=""
                      className="h-11 pr-10 transition-[border-color,box-shadow] duration-200 border-gray-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 hover:border-gray-300 pl-3 pt-4"
                      autoComplete="current-password"
                      {...field}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 focus:text-gray-600 transition-colors"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </FormControl>
                <motion.div
                  initial={false}
                  animate={form.formState.errors.password ? { opacity: 1, y: 0 } : { opacity: 0, y: -10 }}
                >
                  <FormMessage className="text-xs" />
                </motion.div>
              </FormItem>
            )}
          />
          {form.formState.errors.root && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-3 rounded-lg bg-red-50 border border-red-100"
            >
              <p className="text-sm text-red-600">
                {form.formState.errors.root.message}
              </p>
            </motion.div>
          )}
          <div className="relative">
            <motion.div
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
            >
              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 transition-colors duration-300 relative overflow-hidden group"
                disabled={isLoading}
              >
                <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/10 to-white/0 opacity-0 group-hover:opacity-100 transition-opacity" />
                <span className="relative z-10">
                  {isLoading ? (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex items-center justify-center"
                    >
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Logging in...
                    </motion.div>
                  ) : (
                    'Login'
                  )}
                </span>
              </Button>
            </motion.div>
          </div>
        </form>
      </Form>
    </motion.div>
  );
}