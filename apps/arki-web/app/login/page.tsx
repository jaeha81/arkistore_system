"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

// TODO: 로그인 활성화 시 아래 import 복구
// import { useState, type FormEvent } from "react";
// import { authApi } from "@/lib/api";
// import Button from "@/components/ui/Button";
// import Input from "@/components/ui/Input";

// TODO: 로그인 활성화 시 원래 LoginPage 컴포넌트 복구
export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/arki/dashboard");
  }, [router]);

  return null;
}
