"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { issuesApi } from "../../../lib/api";
import { formatDate } from "../../../lib/utils";
import Badge, { statusVariant } from "../../../components/ui/Badge";
import Select from "../../../components/ui/Select";
import { Table, Thead, Tbody, Th, Td, Tr } from "../../../components/ui/Table";
import Spinner from "../../../components/ui/Spinner";

interface IssueGroup {
  id: string;
  group_title: string;
  occurrence_count: number;
  first_seen_at: string;
  last_seen_at: string;
  group_status: string;
}

const statusOptions = [
  { value: "", label: "전체 상태" },
  { value: "new", label: "New" },
  { value: "acknowledged", label: "Acknowledged" },
  { value: "resolved", label: "Resolved" },
];

export default function IssuesPage() {
  const router = useRouter();
  const [groups, setGroups] = useState<IssueGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");

  const fetchGroups = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (statusFilter) params.group_status = statusFilter;
      const res = await issuesApi.listGroups(params);
      const data = res.data;
      setGroups(Array.isArray(data) ? data : data?.items ?? []);
    } catch {
      // handle silently
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    fetchGroups();
  }, [fetchGroups]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-gray-900">오류/이슈 관리</h2>
        <p className="mt-1 text-sm text-gray-500">
          이슈 그룹별로 오류를 관리합니다
        </p>
      </div>

      {/* Filter */}
      <div className="flex items-end gap-3 rounded-xl bg-white p-4 shadow-sm ring-1 ring-gray-200">
        <div className="w-48">
          <Select
            label="상태 필터"
            options={statusOptions}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          />
        </div>
        <div className="text-sm text-gray-500">
          총 <span className="font-semibold text-gray-900">{groups.length}</span>개 이슈 그룹
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <Spinner text="이슈 로딩 중..." />
      ) : groups.length === 0 ? (
        <div className="rounded-xl bg-white py-16 text-center shadow-sm ring-1 ring-gray-200">
          <p className="text-sm text-gray-500">이슈 그룹이 없습니다.</p>
        </div>
      ) : (
        <Table>
          <Thead>
            <tr>
              <Th>이슈 제목</Th>
              <Th>발생 횟수</Th>
              <Th>최초 발생</Th>
              <Th>마지막 발생</Th>
              <Th>상태</Th>
            </tr>
          </Thead>
          <Tbody>
            {groups.map((g) => (
              <Tr
                key={g.id}
                onClick={() => router.push(`/ops/issues/${g.id}`)}
              >
                <Td className="max-w-md truncate font-medium text-gray-900">
                  {g.group_title}
                </Td>
                <Td>
                  <span className="inline-flex items-center justify-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-semibold text-gray-700">
                    {g.occurrence_count}건
                  </span>
                </Td>
                <Td>{formatDate(g.first_seen_at)}</Td>
                <Td>{formatDate(g.last_seen_at)}</Td>
                <Td>
                  <Badge variant={statusVariant(g.group_status)}>
                    {g.group_status}
                  </Badge>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}
    </div>
  );
}
