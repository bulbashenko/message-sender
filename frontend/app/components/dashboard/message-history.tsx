'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface Message {
  id: string;
  created_at: string;
  status: string;
}

interface EmailMessage extends Message {
  to: string;
  subject: string;
  message: string;
}

interface WhatsAppMessage extends Message {
  phone_number: string;
  message: string;
}

export function MessageHistory() {
  const [emailMessages, setEmailMessages] = useState<EmailMessage[]>([]);
  const [whatsappMessages, setWhatsappMessages] = useState<WhatsAppMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const [emailResponse, whatsappResponse] = await Promise.all([
          fetch('/api/communications/email/'),
          fetch('/api/communications/whatsapp/'),
        ]);

        if (!emailResponse.ok || !whatsappResponse.ok) {
          throw new Error('Failed to fetch messages');
        }

        const [emailData, whatsappData] = await Promise.all([
          emailResponse.json(),
          whatsappResponse.json(),
        ]);

        setEmailMessages(emailData);
        setWhatsappMessages(whatsappData);
      } catch (err) {
        setError('Failed to load message history');
        console.error('Error fetching messages:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMessages();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Message History</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-4">Loading messages...</div>
        ) : error ? (
          <div className="text-center text-red-500 py-4">{error}</div>
        ) : (
          <Tabs defaultValue="email" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="email">Email</TabsTrigger>
              <TabsTrigger value="whatsapp">WhatsApp</TabsTrigger>
            </TabsList>
            <TabsContent value="email">
              <div className="space-y-4">
                {emailMessages.length === 0 ? (
                  <div className="text-center py-4 text-gray-500">No email messages found</div>
                ) : (
                  emailMessages.map((msg) => (
                    <div key={msg.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium">To: {msg.to}</p>
                          <p className="text-sm text-gray-600">Subject: {msg.subject}</p>
                        </div>
                        <span className={`text-sm px-2 py-1 rounded ${
                          msg.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {msg.status}
                        </span>
                      </div>
                      <p className="mt-2 text-gray-700">{msg.message}</p>
                      <p className="mt-2 text-sm text-gray-500">{formatDate(msg.created_at)}</p>
                    </div>
                  ))
                )}
              </div>
            </TabsContent>
            <TabsContent value="whatsapp">
              <div className="space-y-4">
                {whatsappMessages.length === 0 ? (
                  <div className="text-center py-4 text-gray-500">No WhatsApp messages found</div>
                ) : (
                  whatsappMessages.map((msg) => (
                    <div key={msg.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <p className="font-medium">To: {msg.phone_number}</p>
                        <span className={`text-sm px-2 py-1 rounded ${
                          msg.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {msg.status}
                        </span>
                      </div>
                      <p className="mt-2 text-gray-700">{msg.message}</p>
                      <p className="mt-2 text-sm text-gray-500">{formatDate(msg.created_at)}</p>
                    </div>
                  ))
                )}
              </div>
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
}