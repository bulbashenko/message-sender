'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Loader2 } from 'lucide-react';
import { register } from '@/app/lib/auth';

const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

interface RegisterFormProps {
  onSuccess: () => void;
}

export function RegisterForm({ onSuccess }: RegisterFormProps) {
  const [isLoading, setIsLoading] = useState(false);
  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: {

      email: '',
      password: '',
    },
  });

  const onSubmit = async (values: RegisterFormValues) => {
    try {
      setIsLoading(true);
      await register(values.email, values.password);
      onSuccess();
    } catch (error: any) {
      console.error('Registration failed:', error);
      
      // Handle specific error cases
      if (error.message?.toLowerCase().includes('email already registered')) {
        form.setError('email', {
          message: 'This email is already registered. Please try logging in instead.',
        });
      } else if (error.message?.toLowerCase().includes('provide both email and password')) {
        // Set errors for empty fields
        if (!values.email) {
          form.setError('email', { message: 'Email is required' });
        }
        if (!values.password) {
          form.setError('password', { message: 'Password is required' });
        }
      } else {
        // For network or unexpected errors, show at form level
        form.setError('root', {
          message: error.message || 'Registration failed. Please try again.',
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input placeholder="Enter your email" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder="Create a password"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {form.formState.errors.root && (
          <div className="text-sm text-red-500">
            {form.formState.errors.root.message}
          </div>
        )}
        <Button
          type="submit"
          className="w-full"
          disabled={isLoading || form.formState.isSubmitting}
          aria-disabled={isLoading || form.formState.isSubmitting}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Creating account...
            </>
          ) : (
            'Create account'
          )}
        </Button>
      </form>
    </Form>
  );
}