"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

// TODO: 로그인 활성화 시 원래 LoginPage 컴포넌트 복구

export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/ops");
  }, [router]);

  return null;
}
