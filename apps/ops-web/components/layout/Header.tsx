"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { LogOut, Menu, User } from "lucide-react";
import { authApi } from "../../lib/api";
import Button from "../ui/Button";

interface HeaderProps {
  onMenuClick?: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const router = useRouter();
  const [userName, setUserName] = useState<string>("");

  useEffect(() => {
    authApi
      .me()
      .then((res) => {
        const data = res.data?.data;
        setUserName(data?.name ?? data?.email ?? "관리자");
      })
      .catch(() => {});
  }, []);

  async function handleLogout() {
    try {
      await authApi.logout();
    } catch {
      // ignore
    }
    router.push("/login");
  }

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-gray-200 bg-white px-4 md:px-6">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="flex h-8 w-8 items-center justify-center rounded-md text-gray-500 transition-colors hover:bg-gray-100 hover:text-gray-700 md:hidden"
          aria-label="메뉴"
        >
          <Menu className="h-5 w-5" />
        </button>
        <h1 className="text-lg font-semibold text-gray-800">
          JH 운영 대시보드
        </h1>
      </div>
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <User className="h-4 w-4" />
          <span className="hidden sm:inline">{userName}</span>
        </div>
        <Button variant="ghost" size="sm" onClick={handleLogout}>
          <LogOut className="h-4 w-4" />
          <span className="hidden sm:inline">로그아웃</span>
        </Button>
      </div>
    </header>
  );
}
