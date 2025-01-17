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

const whatsappSchema = z.object({
  to: z.string()
    .min(10, 'Phone number must be at least 10 digits')
    .regex(/^\+/, 'Phone number must start with + and country code'),
  message: z.string().min(1, 'Message is required'),
});

type WhatsAppFormValues = z.infer<typeof whatsappSchema>;

export function WhatsAppForm() {
  const [isLoading, setIsLoading] = useState(false);

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

      // Show success message from the backend
      alert(data.data.message || 'WhatsApp message sent successfully');
      form.reset();
    } catch (error: any) {
      console.error('WhatsApp send failed:', error);
      // Show error message
      alert(error.message || 'Failed to send WhatsApp message');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Send WhatsApp Message</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="to"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Phone Number</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter phone number with + and country code (e.g. +1234567890)" {...field} />
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
                  <FormLabel>Message</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Type your message here"
                      className="min-h-[100px]"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? 'Sending...' : 'Send Message'}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}