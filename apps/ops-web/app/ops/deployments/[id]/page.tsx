"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { logsApi } from "../../../../lib/api";
import { formatDate } from "../../../../lib/utils";
import Badge, { statusVariant } from "../../../../components/ui/Badge";
import Spinner from "../../../../components/ui/Spinner";

interface DeploymentEvent {
  id: string;
  action_type: string;
  actor_email: string;
  target_table: string | null;
  target_id: string | null;
  created_at: string;
  metadata: {
    project_code?: string;
    version_tag?: string;
    environment?: string;
    status?: string;
    deploy_url?: string;
    commit_sha?: string;
    branch?: string;
    triggered_by?: string;
    duration_seconds?: number;
  } | null;
}

function envVariant(env: string) {
  switch (env) {
    case "production": return "danger" as const;
    case "staging": return "warning" as const;
    case "dev":
    case "development": return "info" as const;
    default: return "default" as const;
  }
}

export default function DeploymentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [event, setEvent] = useState<DeploymentEvent | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    logsApi
      .getEvent(id)
      .then((res) => {
        const data = res.data?.data ?? res.data;
        setEvent(data);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Spinner text="배포 기록 로딩 중..." />;
  if (!event) {
    return (
      <div className="py-16 text-center text-gray-500">
        배포 기록을 찾을 수 없습니다.
      </div>
    );
  }

  const meta = event.metadata ?? {};
  const env = meta.environment ?? "—";
  const status = meta.status ?? "—";

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/ops/deployments")}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="h-4 w-4" />
        배포 목록으로
      </button>

      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-gray-900">
          {meta.project_code ?? "배포 상세"}
        </h2>
        <Badge variant={envVariant(env)}>{env}</Badge>
        <Badge variant={statusVariant(status)}>{status}</Badge>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
        <h3 className="mb-4 font-semibold text-gray-900">배포 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            { label: "프로젝트", value: meta.project_code ?? "—" },
            { label: "버전 태그", value: meta.version_tag ?? "—" },
            { label: "환경", value: env },
            { label: "상태", value: status },
            { label: "브랜치", value: meta.branch ?? "—" },
            { label: "커밋 SHA", value: meta.commit_sha ? meta.commit_sha.slice(0, 8) : "—" },
            { label: "수행자", value: event.actor_email },
            { label: "트리거", value: meta.triggered_by ?? event.actor_email },
            { label: "소요 시간", value: meta.duration_seconds ? `${meta.duration_seconds}초` : "—" },
            { label: "배포 시각", value: formatDate(event.created_at) },
          ].map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-gray-400">{f.label}</dt>
              <dd className="mt-1 text-sm text-gray-900">{f.value}</dd>
            </div>
          ))}
          {meta.deploy_url && (
            <div className="col-span-2">
              <dt className="text-xs font-medium uppercase tracking-wider text-gray-400">배포 URL</dt>
              <dd className="mt-1">
                <a
                  href={meta.deploy_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:underline"
                >
                  {meta.deploy_url}
                </a>
              </dd>
            </div>
          )}
        </dl>
      </div>

      {Object.keys(meta).length > 0 && (
        <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
          <h3 className="mb-4 font-semibold text-gray-900">메타데이터 (원본)</h3>
          <pre className="overflow-x-auto rounded-lg bg-gray-50 p-4 text-xs text-gray-700">
            {JSON.stringify(meta, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
