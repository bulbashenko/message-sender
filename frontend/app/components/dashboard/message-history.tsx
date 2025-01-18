'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { endpoints } from '@/app/lib/config';
import { getAuthHeaders } from '@/app/lib/auth';

interface Message {
  id: string;
  type: 'email' | 'whatsapp';
  status: 'pending' | 'sent' | 'failed';
  recipient: string;
  content: string;
  subject?: string;
  error_message?: string;
  whatsapp_message_id?: string;
  created_at: string;
  sent_at?: string;
}

interface PaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Message[];
}

export function MessageHistory() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nextPage, setNextPage] = useState<string | null>(null);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const fetchMessages = async (url?: string, silent: boolean = false) => {
    try {
      setError(null);
      if (!url) {
        if (!silent) {
          setIsLoading(true);
          setRefreshing(true);
        }
        url = `${endpoints.communications.history}`;
      } else {
        setIsLoadingMore(true);
      }

      const headers = await getAuthHeaders();
      const response = await fetch(url, {
        credentials: 'include',
        headers: {
          ...headers,
          'Accept': 'application/json',
        }
      });
      if (!response.ok) {
        throw new Error('Failed to fetch messages');
      }

      const data: PaginatedResponse = await response.json();
      
      if (url.includes('page=')) {
        // Append new messages for pagination
        setMessages(prev => [...prev, ...data.results]);
      } else {
        // Replace messages
        setMessages(data.results);
      }
      
      setNextPage(data.next);
    } catch (err) {
      setError('Failed to load message history');
      console.error('Error fetching messages:', err);
    } finally {
      if (!silent) setIsLoading(false);
      setRefreshing(false);
      setIsLoadingMore(false);
    }
  };

  useEffect(() => {
    fetchMessages();
    
    // Set up auto-refresh interval
    const refreshInterval = setInterval(() => {
      fetchMessages(undefined, true);
    }, 3000); // Refresh every 3 seconds for more responsive updates

    return () => clearInterval(refreshInterval);
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'sent':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getMessageTypeIcon = (type: 'email' | 'whatsapp') => {
    if (type === 'email') {
      return (
        <svg
          className="w-5 h-5 text-blue-600 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
          />
        </svg>
      );
    }
    return (
      <svg
        className="w-5 h-5 text-green-600 flex-shrink-0"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
        />
      </svg>
    );
  };

  const renderMessage = (msg: Message) => (
    <div key={msg.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
      <div className="flex justify-between items-start">
        <div className="flex items-start space-x-3">
          {getMessageTypeIcon(msg.type)}
          <div>
            <p className="font-medium">To: {msg.recipient}</p>
            {msg.type === 'email' && msg.subject && (
              <p className="text-sm text-gray-600">Subject: {msg.subject}</p>
            )}
          </div>
        </div>
        <span className={`text-sm px-2 py-1 rounded ${getStatusColor(msg.status)}`}>
          {msg.status}
        </span>
      </div>
      <p className="mt-2 text-gray-700 pl-8">{msg.content}</p>
      {msg.error_message && (
        <p className="mt-2 text-sm text-red-600 pl-8">Error: {msg.error_message}</p>
      )}
      <div className="mt-2 text-sm text-gray-500 pl-8">
        <p>Created: {formatDate(msg.created_at)}</p>
        {msg.sent_at && <p>Sent: {formatDate(msg.sent_at)}</p>}
      </div>
    </div>
  );

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Message History</CardTitle>
          {refreshing && (
            <span className="text-sm text-gray-500 animate-pulse">
              Refreshing...
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-4">Loading messages...</div>
        ) : error ? (
          <div className="text-center text-red-500 py-4">{error}</div>
        ) : (
          <div className="space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-4 text-gray-500">
                No messages found
              </div>
            ) : (
              <>
                {messages.map(renderMessage)}
                {nextPage && (
                  <div className="text-center pt-4">
                    <Button
                      onClick={() => fetchMessages(nextPage)}
                      disabled={isLoadingMore}
                      variant="outline"
                    >
                      {isLoadingMore ? 'Loading...' : 'Load More'}
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}