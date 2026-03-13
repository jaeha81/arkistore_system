"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  FolderKanban,
  AlertTriangle,
  Rocket,
  ArrowRight,
} from "lucide-react";
import { projectsApi, issuesApi, logsApi } from "../../lib/api";
import { formatDateShort } from "../../lib/utils";
import Badge, { statusVariant } from "../../components/ui/Badge";
import { Table, Thead, Tbody, Th, Td, Tr } from "../../components/ui/Table";
import Spinner from "../../components/ui/Spinner";

interface SummaryCard {
  label: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  href: string;
}

interface IssueGroup {
  id: string;
  group_title: string;
  occurrence_count: number;
  last_seen_at: string;
  group_status: string;
}

export default function DashboardPage() {
  const [projectCount, setProjectCount] = useState(0);
  const [issueCount, setIssueCount] = useState(0);
  const [deployCount, setDeployCount] = useState(0);
  const [recentIssues, setRecentIssues] = useState<IssueGroup[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [projRes, issueRes, deployRes] = await Promise.allSettled([
          projectsApi.list(),
          issuesApi.listGroups(),
          logsApi.listEvents({ action_type: "deployment.create" }),
        ]);

        if (projRes.status === "fulfilled") {
          const data = projRes.value.data;
          setProjectCount(Array.isArray(data) ? data.length : data?.items?.length ?? 0);
        }
        if (issueRes.status === "fulfilled") {
          const data = issueRes.value.data;
          const items: IssueGroup[] = Array.isArray(data) ? data : data?.items ?? [];
          setIssueCount(items.filter((g: IssueGroup) => g.group_status !== "resolved").length);
          setRecentIssues(items.slice(0, 5));
        }
        if (deployRes.status === "fulfilled") {
          const data = deployRes.value.data;
          const items = Array.isArray(data) ? data : data?.items ?? [];
          // count today's deployments
          const today = new Date().toISOString().split("T")[0];
          setDeployCount(
            items.filter((d: { created_at?: string }) =>
              d.created_at?.startsWith(today)
            ).length
          );
        }
      } catch {
        // silently handle
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const cards: SummaryCard[] = [
    {
      label: "전체 프로젝트",
      value: projectCount,
      icon: <FolderKanban className="h-6 w-6" />,
      color: "bg-blue-50 text-blue-600",
      href: "/ops/projects",
    },
    {
      label: "활성 이슈",
      value: issueCount,
      icon: <AlertTriangle className="h-6 w-6" />,
      color: "bg-amber-50 text-amber-600",
      href: "/ops/issues",
    },
    {
      label: "오늘 배포",
      value: deployCount,
      icon: <Rocket className="h-6 w-6" />,
      color: "bg-emerald-50 text-emerald-600",
      href: "/ops/deployments",
    },
  ];

  if (loading) {
    return <Spinner size="lg" text="대시보드 로딩 중..." />;
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h2 className="text-xl font-bold text-gray-900">대시보드</h2>
        <p className="mt-1 text-sm text-gray-500">
          운영 현황을 한눈에 확인하세요
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {cards.map((card) => (
          <Link
            key={card.label}
            href={card.href}
            className="group rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-200 transition-shadow hover:shadow-md"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">
                  {card.label}
                </p>
                <p className="mt-1 text-3xl font-bold text-gray-900">
                  {card.value}
                </p>
              </div>
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-lg ${card.color}`}
              >
                {card.icon}
              </div>
            </div>
            <div className="mt-3 flex items-center text-xs text-gray-400 group-hover:text-blue-500">
              자세히 보기
              <ArrowRight className="ml-1 h-3 w-3" />
            </div>
          </Link>
        ))}
      </div>

      {/* Recent Issues Table */}
      <div className="rounded-xl bg-white p-5 shadow-sm ring-1 ring-gray-200">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">최근 이슈 그룹</h3>
          <Link
            href="/ops/issues"
            className="text-xs text-blue-600 hover:underline"
          >
            전체 보기 →
          </Link>
        </div>

        {recentIssues.length === 0 ? (
          <p className="py-8 text-center text-sm text-gray-400">
            등록된 이슈가 없습니다.
          </p>
        ) : (
          <Table>
            <Thead>
              <tr>
                <Th>이슈 제목</Th>
                <Th>발생 횟수</Th>
                <Th>마지막 발생</Th>
                <Th>상태</Th>
              </tr>
            </Thead>
            <Tbody>
              {recentIssues.map((issue) => (
                <Tr key={issue.id}>
                  <Td className="font-medium text-gray-900">
                    {issue.group_title}
                  </Td>
                  <Td>{issue.occurrence_count}건</Td>
                  <Td>{formatDateShort(issue.last_seen_at)}</Td>
                  <Td>
                    <Badge variant={statusVariant(issue.group_status)}>
                      {issue.group_status}
                    </Badge>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </div>
    </div>
  );
}
