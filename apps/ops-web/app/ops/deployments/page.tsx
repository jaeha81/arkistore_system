"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { logsApi } from "../../../lib/api";
import { formatDate } from "../../../lib/utils";
import Badge, { statusVariant } from "../../../components/ui/Badge";
import Select from "../../../components/ui/Select";
import { Table, Thead, Tbody, Th, Td, Tr } from "../../../components/ui/Table";
import Spinner from "../../../components/ui/Spinner";

interface Deployment {
  id: string;
  project_code?: string;
  target_id?: string;
  version_tag?: string;
  environment?: string;
  deployed_at?: string;
  created_at?: string;
  status?: string;
  action_type?: string;
  actor_email?: string;
  metadata?: {
    project_code?: string;
    version_tag?: string;
    environment?: string;
    status?: string;
  };
}

const envOptions = [
  { value: "", label: "전체 환경" },
  { value: "dev", label: "Development" },
  { value: "staging", label: "Staging" },
  { value: "production", label: "Production" },
];

export default function DeploymentsPage() {
  const router = useRouter();
  const [deployments, setDeployments] = useState<Deployment[]>([]);
  const [loading, setLoading] = useState(true);
  const [envFilter, setEnvFilter] = useState("");

  const fetchDeployments = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = {
        action_type: "deployment.create",
      };
      if (envFilter) params.environment = envFilter;
      const res = await logsApi.listEvents(params);
      const data = res.data;
      setDeployments(Array.isArray(data) ? data : data?.items ?? []);
    } catch {
      // handle silently
    } finally {
      setLoading(false);
    }
  }, [envFilter]);

  useEffect(() => {
    fetchDeployments();
  }, [fetchDeployments]);

  function getField(d: Deployment, field: "project_code" | "version_tag" | "environment" | "status"): string {
    return d[field] || d.metadata?.[field] || "-";
  }

  function envVariant(env: string) {
    switch (env) {
      case "production":
        return "danger" as const;
      case "staging":
        return "warning" as const;
      case "dev":
      case "development":
        return "info" as const;
      default:
        return "default" as const;
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-gray-900">배포 기록</h2>
        <p className="mt-1 text-sm text-gray-500">
          프로젝트별 배포 이력을 확인합니다
        </p>
      </div>

      {/* Filter */}
      <div className="flex items-end gap-3 rounded-xl bg-white p-4 shadow-sm ring-1 ring-gray-200">
        <div className="w-48">
          <Select
            label="환경 필터"
            options={envOptions}
            value={envFilter}
            onChange={(e) => setEnvFilter(e.target.value)}
          />
        </div>
        <div className="text-sm text-gray-500">
          총{" "}
          <span className="font-semibold text-gray-900">
            {deployments.length}
          </span>
          건의 배포 기록
        </div>
      </div>

      {/* Table */}
      {loading ? (
        <Spinner text="배포 기록 로딩 중..." />
      ) : deployments.length === 0 ? (
        <div className="rounded-xl bg-white py-16 text-center shadow-sm ring-1 ring-gray-200">
          <p className="text-sm text-gray-500">배포 기록이 없습니다.</p>
        </div>
      ) : (
        <Table>
          <Thead>
            <tr>
              <Th>프로젝트</Th>
              <Th>버전</Th>
              <Th>환경</Th>
              <Th>배포 시각</Th>
              <Th>상태</Th>
            </tr>
          </Thead>
          <Tbody>
            {deployments.map((d) => {
              const env = getField(d, "environment");
              const status = getField(d, "status");
              return (
                <Tr
                  key={d.id}
                  onClick={() => router.push(`/ops/deployments/${d.id}`)}
                >
                  <Td className="font-mono text-xs font-semibold text-gray-900">
                    {getField(d, "project_code")}
                  </Td>
                  <Td>
                    <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-700">
                      {getField(d, "version_tag")}
                    </code>
                  </Td>
                  <Td>
                    <Badge variant={envVariant(env)}>{env}</Badge>
                  </Td>
                  <Td>
                    {formatDate(d.deployed_at || d.created_at)}
                  </Td>
                  <Td>
                    <Badge variant={statusVariant(status)}>
                      {status}
                    </Badge>
                  </Td>
                </Tr>
              );
            })}
          </Tbody>
        </Table>
      )}
    </div>
  );
}
