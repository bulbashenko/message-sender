// @/components/DashboardHeader.tsx

"use client";

import React from "react";
import { signOut, useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { ChevronDown, User, LogOut } from "lucide-react";

const DashboardHeader: React.FC = () => {
  const { data: session } = useSession();

  if (!session) {
    return null; // Или можно отобразить другой компонент/сообщение
  }

  return (
    <header className="bg-white dark:bg-gray-800 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          {/* Логотип или название приложения */}
          <div className="flex-shrink-0 flex items-center">
            <span className="text-2xl font-bold text-indigo-600">
              Message Sender
            </span>
          </div>

          {/* Информация о пользователе и кнопка выхода */}
          <div className="flex items-center space-x-4">
            {/* Меню пользователя */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="flex items-center space-x-2 p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
                  aria-label="User Menu"
                >
                  <User className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                  <span className="hidden md:inline-block text-gray-700 dark:text-gray-300">
                    {session.user?.email}
                  </span>
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="end"
                className="w-48 bg-white dark:bg-gray-800 border dark:border-gray-700"
              >
                <DropdownMenuItem
                  onSelect={() => signOut()}
                  className="flex items-center space-x-2"
                >
                  <LogOut className="w-4 h-4 text-red-500" />
                  <span className="text-red-500">Sign out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>

      {/* Мобильное меню */}
      <div className="md:hidden">
        {/* Здесь можно добавить компонент мобильного меню, если он доступен в вашей библиотеке UI */}
      </div>
    </header>
  );
};

export default DashboardHeader;
