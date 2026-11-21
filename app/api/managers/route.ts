import { NextResponse } from "next/server";
import demoData from "@/data/sample.json";

export function GET() {
  return NextResponse.json({ demo: true, disclaimer: demoData.disclaimer, managers: demoData.managers.map(({ holdings, ...manager }) => ({ ...manager, count: holdings.length })) });
}
