"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Plus, Search } from "lucide-react";
import { projectsApi } from "../../../lib/api";
import { formatDate } from "../../../lib/utils";
import Badge, { statusVariant } from "../../../components/ui/Badge";
import Button from "../../../components/ui/Button";
import Input from "../../../components/ui/Input";
import Select from "../../../components/ui/Select";
import { Table, Thead, Tbody, Th, Td, Tr } from "../../../components/ui/Table";
import Spinner from "../../../components/ui/Spinner";

interface Project {
  id: string;
  project_code: string;
  name: string;
  client_name: string;
  status: string;
  operation_mode: string;
  created_at: string;
}

const statusOptions = [
  { value: "", label: "전체 상태" },
  { value: "active", label: "Active" },
  { value: "inactive", label: "Inactive" },
  { value: "maintenance", label: "Maintenance" },
];

const modeOptions = [
  { value: "", label: "전체 모드" },
  { value: "managed", label: "Managed" },
  { value: "self-service", label: "Self-service" },
  { value: "hybrid", label: "Hybrid" },
];

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("");
  const [modeFilter, setModeFilter] = useState("");
  const [search, setSearch] = useState("");

  const fetchProjects = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {};
      if (statusFilter) params.status = statusFilter;
      if (modeFilter) params.operation_mode = modeFilter;
      if (search) params.search = search;
      const res = await projectsApi.list(params);
      const data = res.data;
      setProjects(Array.isArray(data) ? data : data?.items ?? []);
    } catch {
      // handle silently
    } finally {
      setLoading(false);
    }
  }, [statusFilter, modeFilter, search]);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const modeVariant = (mode: string) => {
    switch (mode) {
      case "managed":
        return "info";
      case "self-service":
        return "success";
      case "hybrid":
        return "warning";
      default:
        return "default" as const;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">프로젝트 관리</h2>
          <p className="mt-1 text-sm text-gray-500">
            운영 중인 프로젝트를 관리합니다
          </p>
        </div>
        <Button onClick={() => router.push("/ops/projects/new")}>
          <Plus className="h-4 w-4" />
          새 프로젝트
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-end gap-3 rounded-xl bg-white p-4 shadow-sm ring-1 ring-gray-200">
        <div className="w-48">
          <Select
            options={statusOptions}
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            placeholder="전체 상태"
          />
        </div>
        <div className="w-48">
          <Select
            options={modeOptions}
            value={modeFilter}
            onChange={(e) => setModeFilter(e.target.value)}
            placeholder="전체 모드"
          />
        </div>
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="프로젝트명 또는 코드 검색..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="block w-full rounded-lg border border-gray-300 bg-white py-2 pl-10 pr-3 text-sm text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <Spinner text="프로젝트 로딩 중..." />
      ) : projects.length === 0 ? (
        <div className="rounded-xl bg-white py-16 text-center shadow-sm ring-1 ring-gray-200">
          <FolderEmpty />
          <p className="mt-2 text-sm text-gray-500">
            프로젝트가 없습니다.
          </p>
        </div>
      ) : (
        <Table>
          <Thead>
            <tr>
              <Th>프로젝트 코드</Th>
              <Th>프로젝트명</Th>
              <Th>고객사</Th>
              <Th>상태</Th>
              <Th>운영 모드</Th>
              <Th>생성일</Th>
            </tr>
          </Thead>
          <Tbody>
            {projects.map((p) => (
              <Tr
                key={p.id}
                onClick={() => router.push(`/ops/projects/${p.id}`)}
              >
                <Td className="font-mono text-xs font-semibold text-gray-900">
                  {p.project_code}
                </Td>
                <Td className="font-medium text-gray-900">{p.name}</Td>
                <Td>{p.client_name}</Td>
                <Td>
                  <Badge variant={statusVariant(p.status)}>
                    {p.status}
                  </Badge>
                </Td>
                <Td>
                  <Badge variant={modeVariant(p.operation_mode)}>
                    {p.operation_mode}
                  </Badge>
                </Td>
                <Td>{formatDate(p.created_at)}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}
    </div>
  );
}

function FolderEmpty() {
  return (
    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
      <Plus className="h-6 w-6 text-gray-400" />
    </div>
  );
}
