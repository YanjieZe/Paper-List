import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Paper-List Research OS",
  description: "A personal Robotics research cognition system",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
