"use client";

import { useEffect, useState } from "react";
import {
  dashboardApi,
  deliveriesApi,
  contractsApi,
  purchaseRequestsApi,
  leadsApi,
} from "@/lib/api";
import type { DashboardSummary } from "@/types";
import Spinner from "@/components/ui/Spinner";
import Badge from "@/components/ui/Badge";
import {
  ClipboardList,
  AlertTriangle,
  MessageSquare,
  Truck,
  CalendarClock,
  RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/cn";
import dayjs from "dayjs";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface KpiCard {
  label: string;
  value: number;
  color: "yellow" | "red" | "blue" | "green";
  icon: React.ReactNode;
}

interface DeliveryDay {
  date: string;
  count: number;
}

interface StatusCount {
  name: string;
  value: number;
  color: string;
}

const CONTRACT_COLORS: Record<string, string> = {
  draft: "#f59e0b",
  signed: "#3b82f6",
  confirmed: "#10b981",
  cancelled: "#ef4444",
};

const PR_COLORS: Record<string, string> = {
  requested: "#f59e0b",
  reviewed: "#3b82f6",
  approved: "#10b981",
  rejected: "#ef4444",
  converted_to_order: "#8b5cf6",
};

const CONTRACT_LABELS: Record<string, string> = {
  draft: "초안",
  signed: "서명완료",
  confirmed: "확정",
  cancelled: "취소",
};

const PR_LABELS: Record<string, string> = {
  requested: "요청",
  reviewed: "검토",
  approved: "승인",
  rejected: "반려",
  converted_to_order: "발주전환",
};

function aggregateByStatus(
  items: Record<string, unknown>[],
  key: string,
  labels: Record<string, string>,
  colors: Record<string, string>
): StatusCount[] {
  const counts: Record<string, number> = {};
  for (const item of items) {
    const s = item[key] as string;
    counts[s] = (counts[s] ?? 0) + 1;
  }
  return Object.entries(counts).map(([k, v]) => ({
    name: labels[k] ?? k,
    value: v,
    color: colors[k] ?? "#94a3b8",
  }));
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [recentDeliveries, setRecentDeliveries] = useState<Record<string, unknown>[]>([]);
  const [recentContracts, setRecentContracts] = useState<Record<string, unknown>[]>([]);
  const [deliveryTrend, setDeliveryTrend] = useState<DeliveryDay[]>([]);
  const [contractDist, setContractDist] = useState<StatusCount[]>([]);
  const [prDist, setPrDist] = useState<StatusCount[]>([]);
  const [newLeads, setNewLeads] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  async function fetchAll() {
    setLoading(true);
    try {
      const [sumRes, delRes, conRes, prRes, leadRes] = await Promise.allSettled([
        dashboardApi.summary(),
        deliveriesApi.list({ page_size: 50 }),
        contractsApi.list({ page_size: 100 }),
        purchaseRequestsApi.list({ page_size: 100 }),
        leadsApi.list({ lead_status: "new", page_size: 10 }),
      ]);

      if (sumRes.status === "fulfilled") {
        setSummary(sumRes.value.data?.data ?? sumRes.value.data);
      }

      if (delRes.status === "fulfilled") {
        const allDeliveries: Record<string, unknown>[] = delRes.value.data?.data ?? [];
        setRecentDeliveries(allDeliveries.filter(
          (d) => d.delivery_date === dayjs().format("YYYY-MM-DD")
        ).slice(0, 5));

        const last7Days: DeliveryDay[] = Array.from({ length: 7 }, (_, i) => {
          const date = dayjs().subtract(6 - i, "day").format("YYYY-MM-DD");
          const count = allDeliveries.filter((d) => d.delivery_date === date).length;
          return { date: dayjs(date).format("M/D"), count };
        });
        setDeliveryTrend(last7Days);
      }

      if (conRes.status === "fulfilled") {
        const allContracts: Record<string, unknown>[] = conRes.value.data?.data ?? [];
        setRecentContracts(allContracts.slice(0, 5));
        setContractDist(aggregateByStatus(allContracts, "contract_status", CONTRACT_LABELS, CONTRACT_COLORS));
      }

      if (prRes.status === "fulfilled") {
        const allPr: Record<string, unknown>[] = prRes.value.data?.data ?? [];
        setPrDist(aggregateByStatus(allPr, "pr_status", PR_LABELS, PR_COLORS));
      }

      if (leadRes.status === "fulfilled") {
        setNewLeads(leadRes.value.data?.meta?.total ?? 0);
      }
    } catch {
    } finally {
      setLoading(false);
      setLastUpdated(dayjs().format("HH:mm:ss"));
    }
  }

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 60000);
    return () => clearInterval(interval);
  }, []);

  const colorMap = {
    yellow: { bg: "bg-amber-50", text: "text-amber-700", icon: "text-amber-500" },
    red: { bg: "bg-red-50", text: "text-red-700", icon: "text-red-500" },
    blue: { bg: "bg-blue-50", text: "text-blue-700", icon: "text-blue-500" },
    green: { bg: "bg-emerald-50", text: "text-emerald-700", icon: "text-emerald-500" },
  };

  const kpiCards: KpiCard[] = [
    {
      label: "발주대기",
      value: summary?.purchase_requests_pending ?? 0,
      color: "yellow",
      icon: <ClipboardList className="h-5 w-5" />,
    },
    {
      label: "재고부족",
      value: summary?.low_stock_count ?? 0,
      color: "red",
      icon: <AlertTriangle className="h-5 w-5" />,
    },
    {
      label: "신규문의",
      value: newLeads || (summary?.new_inquiries_count ?? 0),
      color: "blue",
      icon: <MessageSquare className="h-5 w-5" />,
    },
    {
      label: "오늘배송",
      value: summary?.deliveries_today ?? 0,
      color: "green",
      icon: <Truck className="h-5 w-5" />,
    },
    {
      label: "CAPA 잔여",
      value: summary?.capa_remaining_today ?? 0,
      color:
        (summary?.capa_remaining_today ?? 0) > 5
          ? "green"
          : (summary?.capa_remaining_today ?? 0) > 2
            ? "yellow"
            : "red",
      icon: <CalendarClock className="h-5 w-5" />,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-bold text-slate-900">대시보드</h2>
        <div className="flex items-center gap-3">
          {lastUpdated && (
            <span className="text-xs text-slate-400">마지막 업데이트: {lastUpdated}</span>
          )}
          <button
            onClick={fetchAll}
            disabled={loading}
            className="flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-sm text-slate-500 transition-colors hover:bg-slate-100 disabled:opacity-50"
          >
            <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
            새로고침
          </button>
        </div>
      </div>

      {loading && !summary ? (
        <Spinner />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            {kpiCards.map((card) => {
              const c = colorMap[card.color];
              return (
                <div
                  key={card.label}
                  className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
                >
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-slate-500">{card.label}</p>
                    <div className={cn("rounded-lg p-2", c.bg, c.icon)}>{card.icon}</div>
                  </div>
                  <p className={cn("mt-2 text-2xl font-bold", c.text)}>{card.value}</p>
                </div>
              );
            })}
          </div>

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="mb-4 text-sm font-semibold text-slate-800">최근 7일 배송 추이</h3>
              {deliveryTrend.length > 0 ? (
                <ResponsiveContainer width="100%" height={180}>
                  <AreaChart data={deliveryTrend} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="deliveryGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.25} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} allowDecimals={false} />
                    <Tooltip
                      contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
                      formatter={(v: number) => [`${v}건`, "배송"]}
                    />
                    <Area
                      type="monotone"
                      dataKey="count"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      fill="url(#deliveryGrad)"
                      dot={{ r: 3, fill: "#3b82f6" }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-[180px] items-center justify-center text-sm text-slate-400">
                  배송 데이터가 없습니다.
                </div>
              )}
            </div>

            <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="mb-4 text-sm font-semibold text-slate-800">계약 상태 분포</h3>
              {contractDist.length > 0 ? (
                <ResponsiveContainer width="100%" height={180}>
                  <PieChart>
                    <Pie
                      data={contractDist}
                      cx="50%"
                      cy="50%"
                      innerRadius={45}
                      outerRadius={70}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {contractDist.map((entry, i) => (
                        <Cell key={i} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
                      formatter={(v: number, name: string) => [`${v}건`, name]}
                    />
                    <Legend
                      iconType="circle"
                      iconSize={8}
                      wrapperStyle={{ fontSize: 11 }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-[180px] items-center justify-center text-sm text-slate-400">
                  계약 데이터가 없습니다.
                </div>
              )}
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="mb-4 text-sm font-semibold text-slate-800">발주 요청 상태별 현황</h3>
            {prDist.length > 0 ? (
              <ResponsiveContainer width="100%" height={160}>
                <BarChart data={prDist} layout="vertical" margin={{ top: 0, right: 16, left: 8, bottom: 0 }}>
                  <XAxis type="number" tick={{ fontSize: 11, fill: "#94a3b8" }} axisLine={false} tickLine={false} allowDecimals={false} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} width={60} />
                  <Tooltip
                    contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
                    formatter={(v: number) => [`${v}건`]}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {prDist.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-[160px] items-center justify-center text-sm text-slate-400">
                발주 요청 데이터가 없습니다.
              </div>
            )}
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-100 px-5 py-4">
                <h3 className="text-sm font-semibold text-slate-800">오늘 배송 현황</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-100">
                  <thead className="bg-slate-50">
                    <tr>
                      {["배송번호", "시간대", "팀", "상태"].map((h) => (
                        <th key={h} className="px-4 py-2 text-left text-xs font-semibold text-slate-500">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {recentDeliveries.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-400">
                          오늘 배송 건이 없습니다.
                        </td>
                      </tr>
                    ) : (
                      recentDeliveries.map((d, i) => (
                        <tr key={i}>
                          <td className="px-4 py-2 text-sm text-slate-700">{(d.delivery_number as string) ?? "—"}</td>
                          <td className="px-4 py-2 text-sm text-slate-600">{d.time_slot as string}</td>
                          <td className="px-4 py-2 text-sm text-slate-600">{d.delivery_team as string}</td>
                          <td className="px-4 py-2">
                            <Badge status={d.delivery_status as string}>{d.delivery_status as string}</Badge>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-100 px-5 py-4">
                <h3 className="text-sm font-semibold text-slate-800">최근 계약</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-100">
                  <thead className="bg-slate-50">
                    <tr>
                      {["계약번호", "날짜", "금액", "상태"].map((h) => (
                        <th key={h} className="px-4 py-2 text-left text-xs font-semibold text-slate-500">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {recentContracts.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-4 py-6 text-center text-sm text-slate-400">
                          최근 계약이 없습니다.
                        </td>
                      </tr>
                    ) : (
                      recentContracts.map((c, i) => (
                        <tr key={i}>
                          <td className="px-4 py-2 text-sm text-slate-700">{(c.contract_number as string) ?? "—"}</td>
                          <td className="px-4 py-2 text-sm text-slate-600">{c.contract_date as string}</td>
                          <td className="px-4 py-2 text-sm text-slate-600">
                            {Number(c.contract_amount ?? 0).toLocaleString()}원
                          </td>
                          <td className="px-4 py-2">
                            <Badge status={c.contract_status as string}>{c.contract_status as string}</Badge>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
