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

const whatsappSchema = z.object({
  to: z.string()
    .min(10, 'Phone number must be at least 10 digits')
    .regex(/^\+/, 'Phone number must start with + and country code'),
  message: z.string().min(1, 'Message is required'),
});

type WhatsAppFormValues = z.infer<typeof whatsappSchema>;

export function WhatsAppForm() {
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const form = useForm<WhatsAppFormValues>({
    resolver: zodResolver(whatsappSchema),
    defaultValues: {
      to: '',
      message: '',
    },
  });

  const onSubmit = async (values: WhatsAppFormValues) => {
    try {
      setIsLoading(true);
      const headers = await getAuthHeaders();
      const response = await fetch(endpoints.whatsapp.send, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          to: values.to,
          message: values.message,
        }),
      });

      const data = await response.json();
      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to send WhatsApp message');
      }

      // Show success toast
      toast({
        title: "Message Sent",
        description: data.data.message || 'WhatsApp message sent successfully',
        variant: "default",
        className: "bg-green-50 border border-green-100 text-green-800",
        duration: 3000,
      });
      
      form.reset();
    } catch (error: any) {
      console.error('WhatsApp send failed:', error);
      // Show error toast
      toast({
        title: "Failed to Send",
        description: error.message || 'Failed to send WhatsApp message',
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
      <CardHeader className="bg-gradient-to-r from-green-50 via-emerald-50 to-white border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <svg
            className="w-6 h-6 text-green-600"
            fill="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20ZM13 7H11V13H17V11H13V7Z" />
          </svg>
          <div>
            <CardTitle className="text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              Send WhatsApp Message
            </CardTitle>
            <p className="text-sm text-gray-600 mt-1">Send instant messages to your contacts</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-6 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-white/50 to-green-50/20 pointer-events-none" />
        <div className="relative z-10">
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="to"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-gray-700 font-medium">Phone Number</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Input 
                          placeholder="Enter phone number with + and country code (e.g. +1234567890)" 
                          className="pl-10 bg-white/70 focus:bg-white focus:ring-2 focus:ring-green-500/20 transition-all duration-200"
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
                            d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
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
                            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
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
                className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white shadow-md hover:shadow-lg transition-all duration-200"
                disabled={isLoading}
              >
                {isLoading ? 'Sending...' : 'Send Message'}
              </Button>
            </form>
          </Form>
        </div>
      </CardContent>
    </Card>
  );
}