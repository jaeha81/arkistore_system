"use client";

import { useEffect, useState, useMemo, type FormEvent } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Github, RefreshCw } from "lucide-react";
import { issuesApi } from "../../../../lib/api";
import { formatDate } from "../../../../lib/utils";
import Badge, { statusVariant } from "../../../../components/ui/Badge";
import Button from "../../../../components/ui/Button";
import Input from "../../../../components/ui/Input";
import Select from "../../../../components/ui/Select";
import { Table, Thead, Tbody, Th, Td, Tr } from "../../../../components/ui/Table";
import Spinner from "../../../../components/ui/Spinner";

interface IssueGroup {
  id: string;
  group_title: string;
  occurrence_count: number;
  first_seen_at: string;
  last_seen_at: string;
  group_status: string;
  github_issue_number: number | null;
  github_issue_url: string | null;
}

interface Issue {
  id: string;
  project_code: string;
  error_code: string;
  screen_name: string;
  message: string;
  severity: string;
  occurred_at: string;
}

export default function IssueGroupDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [group, setGroup] = useState<IssueGroup | null>(null);
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState("");
  const [savingStatus, setSavingStatus] = useState(false);
  const [showGithubForm, setShowGithubForm] = useState(false);
  const [githubForm, setGithubForm] = useState({ title: "", body: "" });
  const [githubLoading, setGithubLoading] = useState(false);

  const idempotencyKey = useMemo(() => crypto.randomUUID(), []);

  useEffect(() => {
    async function load() {
      try {
        const [groupRes, issuesRes] = await Promise.allSettled([
          issuesApi.getGroup(id),
          issuesApi.listByGroup(id),
        ]);
        if (groupRes.status === "fulfilled") {
          const data = groupRes.value.data?.data ?? groupRes.value.data;
          setGroup(data);
          setNewStatus(data?.group_status ?? "new");
          setGithubForm((p) => ({ ...p, title: data?.group_title ?? "" }));
        }
        if (issuesRes.status === "fulfilled") {
          const data = issuesRes.value.data;
          setIssues(Array.isArray(data) ? data : data?.items ?? data?.data ?? []);
        }
      } catch {
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  async function handleStatusUpdate() {
    if (!group) return;
    setSavingStatus(true);
    try {
      await issuesApi.updateGroupStatus(id, { group_status: newStatus });
      setGroup((prev) => prev ? { ...prev, group_status: newStatus } : prev);
    } catch {
    } finally {
      setSavingStatus(false);
    }
  }

  async function handleCreateGithubIssue(e: FormEvent) {
    e.preventDefault();
    setGithubLoading(true);
    try {
      await issuesApi.createGithubIssue(id, githubForm, idempotencyKey);
      setShowGithubForm(false);
      const res = await issuesApi.getGroup(id);
      const data = res.data?.data ?? res.data;
      setGroup(data);
    } catch {
    } finally {
      setGithubLoading(false);
    }
  }

  if (loading) return <Spinner text="이슈 그룹 로딩 중..." />;
  if (!group) {
    return (
      <div className="py-16 text-center text-gray-500">
        이슈 그룹을 찾을 수 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/ops/issues")}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="h-4 w-4" />
        이슈 목록으로
      </button>

      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <h2 className="text-xl font-bold text-gray-900">{group.group_title}</h2>
          <div className="flex items-center gap-2">
            <Badge variant={statusVariant(group.group_status)}>{group.group_status}</Badge>
            <span className="text-sm text-gray-500">
              총 {group.occurrence_count}건 발생
            </span>
          </div>
        </div>
        {group.github_issue_url ? (
          <a
            href={group.github_issue_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 rounded-lg bg-gray-900 px-3 py-2 text-sm font-medium text-white hover:bg-gray-700"
          >
            <Github className="h-4 w-4" />
            GitHub #{group.github_issue_number}
          </a>
        ) : (
          <Button
            size="sm"
            variant="secondary"
            onClick={() => setShowGithubForm(!showGithubForm)}
          >
            <Github className="h-4 w-4" />
            GitHub 이슈 생성
          </Button>
        )}
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
        <h3 className="mb-4 font-semibold text-gray-900">그룹 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            { label: "최초 발생", value: formatDate(group.first_seen_at) },
            { label: "마지막 발생", value: formatDate(group.last_seen_at) },
            { label: "총 발생 횟수", value: `${group.occurrence_count}건` },
            { label: "현재 상태", value: group.group_status },
          ].map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-gray-400">{f.label}</dt>
              <dd className="mt-1 text-sm text-gray-900">{f.value}</dd>
            </div>
          ))}
        </dl>
      </div>

      {showGithubForm && (
        <form
          onSubmit={handleCreateGithubIssue}
          className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200 space-y-4"
        >
          <h3 className="font-semibold text-gray-900">GitHub 이슈 생성</h3>
          <Input
            label="이슈 제목"
            value={githubForm.title}
            onChange={(e) => setGithubForm((p) => ({ ...p, title: e.target.value }))}
            required
          />
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">본문</label>
            <textarea
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-500"
              rows={4}
              value={githubForm.body}
              onChange={(e) => setGithubForm((p) => ({ ...p, body: e.target.value }))}
              placeholder="이슈 상세 내용..."
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="secondary" size="sm" onClick={() => setShowGithubForm(false)}>
              취소
            </Button>
            <Button type="submit" size="sm" loading={githubLoading}>
              <Github className="h-4 w-4" />
              생성
            </Button>
          </div>
        </form>
      )}

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">상태 변경</h3>
        </div>
        <div className="flex items-center gap-3">
          <Select
            options={[
              { value: "new", label: "New" },
              { value: "acknowledged", label: "Acknowledged" },
              { value: "resolved", label: "Resolved" },
            ]}
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
          />
          <Button
            size="sm"
            onClick={handleStatusUpdate}
            loading={savingStatus}
            disabled={newStatus === group.group_status}
          >
            <RefreshCw className="h-4 w-4" />
            상태 변경
          </Button>
        </div>
      </div>

      <div className="rounded-xl bg-white shadow-sm ring-1 ring-gray-200">
        <div className="border-b border-gray-200 p-4">
          <h3 className="font-semibold text-gray-900">
            개별 이슈 목록 ({issues.length}건)
          </h3>
        </div>
        {issues.length === 0 ? (
          <p className="py-8 text-center text-sm text-gray-400">개별 이슈가 없습니다.</p>
        ) : (
          <Table>
            <Thead>
              <tr>
                <Th>프로젝트</Th>
                <Th>오류 코드</Th>
                <Th>화면명</Th>
                <Th>심각도</Th>
                <Th>발생 시각</Th>
              </tr>
            </Thead>
            <Tbody>
              {issues.map((issue) => (
                <Tr key={issue.id}>
                  <Td className="font-mono text-xs font-semibold text-gray-900">
                    {issue.project_code}
                  </Td>
                  <Td>
                    <Badge variant="danger">{issue.error_code}</Badge>
                  </Td>
                  <Td>{issue.screen_name || "—"}</Td>
                  <Td>
                    <Badge variant={statusVariant(issue.severity)}>{issue.severity}</Badge>
                  </Td>
                  <Td>{formatDate(issue.occurred_at)}</Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        )}
      </div>
    </div>
  );
}
