"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Globe,
  Plus,
  ExternalLink,
} from "lucide-react";
import { projectsApi } from "../../../../lib/api";
import { formatDate } from "../../../../lib/utils";
import Badge, { statusVariant } from "../../../../components/ui/Badge";
import Button from "../../../../components/ui/Button";
import Input from "../../../../components/ui/Input";
import Select from "../../../../components/ui/Select";
import { Table, Thead, Tbody, Th, Td, Tr } from "../../../../components/ui/Table";
import Spinner from "../../../../components/ui/Spinner";

interface Project {
  id: string;
  project_code: string;
  name: string;
  client_name: string;
  service_type: string;
  main_url: string;
  status: string;
  operation_mode: string;
  created_at: string;
  updated_at: string;
}

interface Site {
  id: string;
  site_code: string;
  site_name: string;
  site_type: string;
  url: string;
}

interface SiteForm {
  site_code: string;
  site_name: string;
  site_type: string;
  url: string;
}

const siteTypeOptions = [
  { value: "main", label: "Main" },
  { value: "admin", label: "Admin" },
  { value: "api", label: "API" },
  { value: "cdn", label: "CDN" },
  { value: "staging", label: "Staging" },
];

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [sites, setSites] = useState<Site[]>([]);
  const [loading, setLoading] = useState(true);
  const [showSiteForm, setShowSiteForm] = useState(false);
  const [siteLoading, setSiteLoading] = useState(false);
  const [siteForm, setSiteForm] = useState<SiteForm>({
    site_code: "",
    site_name: "",
    site_type: "main",
    url: "",
  });

  useEffect(() => {
    async function load() {
      try {
        const [projRes, sitesRes] = await Promise.allSettled([
          projectsApi.get(id),
          projectsApi.listSites(id),
        ]);

        if (projRes.status === "fulfilled") {
          setProject(projRes.value.data);
        }
        if (sitesRes.status === "fulfilled") {
          const data = sitesRes.value.data;
          setSites(Array.isArray(data) ? data : data?.items ?? []);
        }
      } catch {
        // handle silently
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  async function handleAddSite(e: FormEvent) {
    e.preventDefault();
    if (!siteForm.site_code || !siteForm.site_name || !siteForm.url) return;

    setSiteLoading(true);
    try {
      await projectsApi.createSite(id, siteForm);
      // reload sites
      const res = await projectsApi.listSites(id);
      const data = res.data;
      setSites(Array.isArray(data) ? data : data?.items ?? []);
      setSiteForm({ site_code: "", site_name: "", site_type: "main", url: "" });
      setShowSiteForm(false);
    } catch {
      // handle silently
    } finally {
      setSiteLoading(false);
    }
  }

  if (loading) return <Spinner size="lg" text="프로젝트 로딩 중..." />;
  if (!project) {
    return (
      <div className="py-16 text-center text-gray-500">
        프로젝트를 찾을 수 없습니다.
      </div>
    );
  }

  const infoFields = [
    { label: "프로젝트 코드", value: project.project_code },
    { label: "프로젝트명", value: project.name },
    { label: "고객사", value: project.client_name },
    { label: "서비스 유형", value: project.service_type },
    { label: "메인 URL", value: project.main_url, isLink: true },
    { label: "생성일", value: formatDate(project.created_at) },
    { label: "수정일", value: formatDate(project.updated_at) },
  ];

  return (
    <div className="space-y-6">
      {/* Back */}
      <button
        onClick={() => router.push("/ops/projects")}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="h-4 w-4" />
        프로젝트 목록으로
      </button>

      {/* Header */}
      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-gray-900">{project.name}</h2>
        <Badge variant={statusVariant(project.status)}>
          {project.status}
        </Badge>
        <Badge variant={statusVariant(project.operation_mode)}>
          {project.operation_mode}
        </Badge>
      </div>

      {/* Info Card */}
      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
        <h3 className="mb-4 font-semibold text-gray-900">프로젝트 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {infoFields.map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-gray-400">
                {f.label}
              </dt>
              <dd className="mt-1 text-sm text-gray-900">
                {f.isLink ? (
                  <a
                    href={f.value}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-blue-600 hover:underline"
                  >
                    {f.value}
                    <ExternalLink className="h-3 w-3" />
                  </a>
                ) : (
                  f.value || "-"
                )}
              </dd>
            </div>
          ))}
        </dl>
      </div>

      {/* Sites Section */}
      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold text-gray-900">
            <Globe className="mr-2 inline h-4 w-4" />
            사이트 목록
          </h3>
          <Button
            size="sm"
            variant={showSiteForm ? "secondary" : "primary"}
            onClick={() => setShowSiteForm(!showSiteForm)}
          >
            <Plus className="h-4 w-4" />
            사이트 추가
          </Button>
        </div>

        {/* Inline Add Form */}
        {showSiteForm && (
          <form
            onSubmit={handleAddSite}
            className="mb-4 rounded-lg bg-gray-50 p-4 ring-1 ring-gray-200"
          >
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
              <Input
                placeholder="사이트 코드"
                value={siteForm.site_code}
                onChange={(e) =>
                  setSiteForm((p) => ({ ...p, site_code: e.target.value }))
                }
              />
              <Input
                placeholder="사이트 이름"
                value={siteForm.site_name}
                onChange={(e) =>
                  setSiteForm((p) => ({ ...p, site_name: e.target.value }))
                }
              />
              <Select
                options={siteTypeOptions}
                value={siteForm.site_type}
                onChange={(e) =>
                  setSiteForm((p) => ({ ...p, site_type: e.target.value }))
                }
              />
              <Input
                placeholder="https://..."
                value={siteForm.url}
                onChange={(e) =>
                  setSiteForm((p) => ({ ...p, url: e.target.value }))
                }
              />
            </div>
            <div className="mt-3 flex justify-end gap-2">
              <Button
                type="button"
                size="sm"
                variant="secondary"
                onClick={() => setShowSiteForm(false)}
              >
                취소
              </Button>
              <Button type="submit" size="sm" loading={siteLoading}>
                추가
              </Button>
            </div>
          </form>
        )}

        {/* Sites Table */}
        {sites.length === 0 ? (
          <p className="py-8 text-center text-sm text-gray-400">
            등록된 사이트가 없습니다.
          </p>
        ) : (
          <Table>
            <Thead>
              <tr>
                <Th>사이트 코드</Th>
                <Th>사이트명</Th>
                <Th>유형</Th>
                <Th>URL</Th>
              </tr>
            </Thead>
            <Tbody>
              {sites.map((s) => (
                <Tr key={s.id}>
                  <Td className="font-mono text-xs font-semibold">
                    {s.site_code}
                  </Td>
                  <Td className="font-medium text-gray-900">
                    {s.site_name}
                  </Td>
                  <Td>
                    <Badge variant="info">{s.site_type}</Badge>
                  </Td>
                  <Td>
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-blue-600 hover:underline"
                    >
                      {s.url}
                      <ExternalLink className="h-3 w-3" />
                    </a>
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
