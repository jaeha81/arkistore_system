import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JH Ops Dashboard",
  description: "JH Customer Management Solution - Operations Dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="bg-gray-50 text-gray-900">{children}</body>
    </html>
  );
}
