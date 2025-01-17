'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface PasswordStrengthProps {
  password: string;
}

export function PasswordStrength({ password }: PasswordStrengthProps) {
  const [strength, setStrength] = useState(0);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const calculateStrength = (pwd: string) => {
      let score = 0;
      if (!pwd) return 0;

      // Length check
      if (pwd.length >= 8) score += 1;
      if (pwd.length >= 12) score += 1;

      // Character variety checks
      if (/[A-Z]/.test(pwd)) score += 1;
      if (/[a-z]/.test(pwd)) score += 1;
      if (/[0-9]/.test(pwd)) score += 1;
      if (/[^A-Za-z0-9]/.test(pwd)) score += 1;

      return Math.min(score, 5);
    };

    const getStrengthMessage = (score: number) => {
      switch (score) {
        case 0:
          return 'Too weak';
        case 1:
          return 'Weak';
        case 2:
          return 'Fair';
        case 3:
          return 'Good';
        case 4:
          return 'Strong';
        case 5:
          return 'Very strong';
        default:
          return '';
      }
    };

    const newStrength = calculateStrength(password);
    setStrength(newStrength);
    setMessage(getStrengthMessage(newStrength));
  }, [password]);

  const strengthColors = {
    0: 'bg-gray-200',
    1: 'bg-red-500',
    2: 'bg-orange-500',
    3: 'bg-yellow-500',
    4: 'bg-green-500',
    5: 'bg-emerald-500',
  };

  return (
    <div className="space-y-2">
      <div className="flex h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
        <motion.div
          className={`${strengthColors[strength as keyof typeof strengthColors]}`}
          initial={{ width: '0%' }}
          animate={{ width: `${(strength / 5) * 100}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>
      <p className={`text-xs ${strength > 2 ? 'text-green-600' : 'text-red-500'}`}>
        {message}
      </p>
    </div>
  );
}