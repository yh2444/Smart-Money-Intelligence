import { NextRequest, NextResponse } from "next/server";
import demoData from "@/data/sample.json";

export function GET(request: NextRequest) {
  const ticker = request.nextUrl.searchParams.get("ticker")?.toUpperCase();
  const managerId = request.nextUrl.searchParams.get("manager");
  const records = demoData.managers.flatMap((manager) => manager.holdings.map((position) => ({ ...position, managerId: manager.id, managerName: manager.name })));
  return NextResponse.json({ demo: true, disclaimer: demoData.disclaimer, holdings: records.filter((r) => (!ticker || r.ticker === ticker) && (!managerId || r.managerId === managerId)) });
}
