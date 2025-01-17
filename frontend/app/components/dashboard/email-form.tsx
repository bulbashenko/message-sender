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

      // Show success message
      alert('Email sent successfully');
      form.reset();
    } catch (error: any) {
      console.error('Email send failed:', error);
      // Show error message
      alert(error.message || 'Failed to send email');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Send Email</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="to"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>To</FormLabel>
                  <FormControl>
                    <Input placeholder="recipient@example.com" {...field} />
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
                  <FormLabel>Subject</FormLabel>
                  <FormControl>
                    <Input placeholder="Enter email subject" {...field} />
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
              {isLoading ? 'Sending...' : 'Send Email'}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}