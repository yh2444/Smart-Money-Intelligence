import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Smart Money Intelligence | Demo",
  description: "Prototype for research into public institutional holdings and estimated cost basis. All portfolio data shown is synthetic.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
