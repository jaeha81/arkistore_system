"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { projectsApi } from "../../../../lib/api";
import Input from "../../../../components/ui/Input";
import Select from "../../../../components/ui/Select";
import Button from "../../../../components/ui/Button";

interface FormData {
  project_code: string;
  name: string;
  client_name: string;
  service_type: string;
  main_url: string;
  status: string;
  operation_mode: string;
}

interface FormErrors {
  [key: string]: string;
}

const statusOptions = [
  { value: "active", label: "Active" },
  { value: "inactive", label: "Inactive" },
  { value: "maintenance", label: "Maintenance" },
];

const modeOptions = [
  { value: "managed", label: "Managed" },
  { value: "self-service", label: "Self-service" },
  { value: "hybrid", label: "Hybrid" },
];

const serviceTypeOptions = [
  { value: "website", label: "Website" },
  { value: "ecommerce", label: "E-Commerce" },
  { value: "webapp", label: "Web App" },
  { value: "mobile", label: "Mobile App" },
  { value: "api", label: "API Service" },
];

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [errors, setErrors] = useState<FormErrors>({});
  const [form, setForm] = useState<FormData>({
    project_code: "",
    name: "",
    client_name: "",
    service_type: "website",
    main_url: "",
    status: "active",
    operation_mode: "managed",
  });

  function updateField(field: keyof FormData, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  }

  function validate(): boolean {
    const newErrors: FormErrors = {};
    if (!form.project_code.trim())
      newErrors.project_code = "프로젝트 코드를 입력하세요";
    if (!form.name.trim())
      newErrors.name = "프로젝트명을 입력하세요";
    if (!form.client_name.trim())
      newErrors.client_name = "고객사명을 입력하세요";
    if (!form.main_url.trim())
      newErrors.main_url = "메인 URL을 입력하세요";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    if (!validate()) return;

    setLoading(true);
    try {
      await projectsApi.create(form);
      router.push("/ops/projects");
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(
        axiosErr.response?.data?.detail || "프로젝트 생성에 실패했습니다."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      {/* Back */}
      <button
        onClick={() => router.back()}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"
      >
        <ArrowLeft className="h-4 w-4" />
        프로젝트 목록으로
      </button>

      {/* Header */}
      <div>
        <h2 className="text-xl font-bold text-gray-900">새 프로젝트 등록</h2>
        <p className="mt-1 text-sm text-gray-500">
          새로운 운영 프로젝트를 등록합니다
        </p>
      </div>

      {/* Form */}
      <form
        onSubmit={handleSubmit}
        className="space-y-5 rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-200"
      >
        {error && (
          <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700 ring-1 ring-inset ring-red-200">
            {error}
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <Input
            label="프로젝트 코드"
            placeholder="예: PRJ-001"
            value={form.project_code}
            onChange={(e) => updateField("project_code", e.target.value)}
            error={errors.project_code}
          />
          <Input
            label="프로젝트명"
            placeholder="프로젝트 이름"
            value={form.name}
            onChange={(e) => updateField("name", e.target.value)}
            error={errors.name}
          />
        </div>

        <Input
          label="고객사명"
          placeholder="고객사 이름"
          value={form.client_name}
          onChange={(e) => updateField("client_name", e.target.value)}
          error={errors.client_name}
        />

        <Input
          label="메인 URL"
          placeholder="https://example.com"
          value={form.main_url}
          onChange={(e) => updateField("main_url", e.target.value)}
          error={errors.main_url}
        />

        <div className="grid grid-cols-3 gap-4">
          <Select
            label="서비스 유형"
            options={serviceTypeOptions}
            value={form.service_type}
            onChange={(e) => updateField("service_type", e.target.value)}
          />
          <Select
            label="상태"
            options={statusOptions}
            value={form.status}
            onChange={(e) => updateField("status", e.target.value)}
          />
          <Select
            label="운영 모드"
            options={modeOptions}
            value={form.operation_mode}
            onChange={(e) => updateField("operation_mode", e.target.value)}
          />
        </div>

        <div className="flex justify-end gap-3 border-t border-gray-100 pt-5">
          <Button
            type="button"
            variant="secondary"
            onClick={() => router.back()}
          >
            취소
          </Button>
          <Button type="submit" loading={loading}>
            프로젝트 등록
          </Button>
        </div>
      </form>
    </div>
  );
}
