'use client';

import { WhatsAppForm } from '@/app/components/dashboard/whatsapp-form';
import { EmailForm } from '@/app/components/dashboard/email-form';

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="w-full">
          <WhatsAppForm />
        </div>
        <div className="w-full">
          <EmailForm />
        </div>
      </div>
    </div>
  );
}