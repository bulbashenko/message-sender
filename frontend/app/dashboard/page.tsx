'use client';

import { WhatsAppForm } from '@/app/components/dashboard/whatsapp-form';
import { EmailForm } from '@/app/components/dashboard/email-form';
import { motion } from 'framer-motion';

const containerVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
      delayChildren: 0.3
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { 
    opacity: 1, 
    y: 0,
    transition: {
      type: "spring",
      stiffness: 100,
      damping: 15
    }
  }
};

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white relative overflow-hidden">
      {/* Background patterns */}
      <div className="absolute inset-0 overflow-hidden opacity-50">
        <div className="absolute top-0 left-0 w-full h-full bg-grid-pattern" />
        <div className="absolute inset-0 bg-gradient-to-b from-white/50 via-transparent to-white/50" />
      </div>
      
      <div className="container mx-auto px-4 py-8 space-y-8 relative">
        {/* Enhanced Header Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, type: "spring" }}
          className="bg-white rounded-xl shadow-xl p-8 border border-gray-200 relative overflow-hidden hover:shadow-2xl transition-all duration-300 group"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-blue-50 via-purple-50 to-pink-50 opacity-50 group-hover:opacity-70 transition-opacity duration-300" />
          <div className="absolute inset-0 bg-grid-pattern opacity-5 group-hover:opacity-10 transition-opacity duration-300" />
          <div className="relative z-10">
            <motion.div 
              className="flex items-center space-x-3"
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              <motion.svg
                whileHover={{ scale: 1.2, rotate: 180 }}
                transition={{ type: "spring", stiffness: 300 }}
                className="w-8 h-8 text-blue-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16m-7 6h7"
                />
              </motion.svg>
              <motion.h1 
                className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 bg-clip-text text-transparent bg-300 animate-gradient"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                Dashboard
              </motion.h1>
            </motion.div>
            <motion.p 
              className="mt-2 text-gray-600 font-medium"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              Manage your communications in one place
            </motion.p>
          </div>
        </motion.div>

        {/* Enhanced Grid Layout */}
        <motion.div 
          variants={containerVariants}
          initial="hidden"
          animate="show"
          className="grid grid-cols-1 md:grid-cols-2 gap-8"
        >
          <motion.div 
            variants={itemVariants}
            className="w-full group"
          >
            <div className="transform-gpu transition-all duration-300 ease-out group-hover:translate-y-[-4px] group-hover:shadow-xl relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <WhatsAppForm />
            </div>
          </motion.div>
          <motion.div 
            variants={itemVariants}
            className="w-full group"
          >
            <div className="transform-gpu transition-all duration-300 ease-out group-hover:translate-y-[-4px] group-hover:shadow-xl relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 to-pink-500/5 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <EmailForm />
            </div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}