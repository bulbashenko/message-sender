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
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { endpoints } from '@/app/lib/config';
import { getAuthHeaders } from '@/app/lib/auth';
import { useToast } from '@/hooks/use-toast';

const emailSchema = z.object({
  to: z.string().email('Invalid email address'),
  subject: z.string()
    .min(1, 'Subject is required')
    .max(255, 'Subject cannot be longer than 255 characters'),
  message: z.string().min(1, 'Message is required'),
});

type EmailFormValues = z.infer<typeof emailSchema>;

export function EmailForm() {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const form = useForm<EmailFormValues>({
    resolver: zodResolver(emailSchema),
    defaultValues: {
      to: '',
      subject: '',
      message: '',
    },
  });

  const onSubmit = async (values: EmailFormValues) => {
    try {
      setIsLoading(true);
      const headers = await getAuthHeaders();
      const response = await fetch(endpoints.email.send, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          to: values.to,
          subject: values.subject,
          message: values.message,
        }),
      });

      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to send email');
      }

      // Show success toast
      toast({
        title: "Email Sent",
        description: "Email sent successfully",
        variant: "default",
        className: "bg-blue-50 border border-blue-100 text-blue-800",
        duration: 3000,
      });
      
      form.reset();
    } catch (error: any) {
      console.error('Email send failed:', error);
      // Show error toast
      toast({
        title: "Failed to Send",
        description: error.message || 'Failed to send email',
        variant: "destructive",
        className: "bg-red-50 border border-red-100",
        duration: 4000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="border border-gray-200 shadow-md hover:shadow-lg transition-shadow duration-300 ease-out bg-white/50 backdrop-blur-sm will-change-transform">
      <CardHeader className="bg-gradient-to-r from-blue-50 via-indigo-50 to-white border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <svg
            className="w-6 h-6 text-blue-600"
            fill="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z" />
          </svg>
          <div>
            <CardTitle className="text-xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Send Email
            </CardTitle>
            <p className="text-sm text-gray-600 mt-1">Send emails to your contacts</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-6 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-white/50 to-blue-50/20 pointer-events-none" />
        <div className="relative z-10">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="to"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-gray-700 font-medium">To</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Input 
                          placeholder="recipient@example.com" 
                          className="pl-10 bg-white/70 focus:bg-white focus:ring-2 focus:ring-blue-500/20 transition-all duration-200"
                          {...field} 
                        />
                        <svg
                          className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207"
                          />
                        </svg>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="subject"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-gray-700 font-medium">Subject</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Input 
                          placeholder="Enter email subject" 
                          className="pl-10 bg-white/70 focus:bg-white transition-colors duration-200"
                          {...field} 
                        />
                        <svg
                          className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"
                          />
                        </svg>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="message"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-gray-700 font-medium">Message</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Textarea 
                          placeholder="Type your message here"
                          className="min-h-[100px] pl-10 bg-white/70 focus:bg-white transition-colors duration-200"
                          {...field}
                        />
                        <svg
                          className="w-5 h-5 text-gray-400 absolute left-3 top-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                          />
                        </svg>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-md hover:shadow-lg transition-all duration-200"
                disabled={isLoading}
              >
                {isLoading ? 'Sending...' : 'Send Email'}
              </Button>
            </form>
          </Form>
        </div>
      </CardContent>
    </Card>
  );
}