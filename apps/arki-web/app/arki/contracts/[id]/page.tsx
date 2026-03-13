"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Paperclip } from "lucide-react";
import { contractsApi } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import dayjs from "dayjs";

interface Contract {
  id: string;
  contract_number: string | null;
  customer_id: string;
  customer_name: string | null;
  consultation_id: string | null;
  contract_date: string;
  contract_amount: number;
  deposit_amount: number | null;
  contract_status: string;
  delivery_required: boolean;
  remarks: string | null;
  created_at: string;
  updated_at: string;
}

interface Attachment {
  id: string;
  file_name: string;
  file_url: string;
  uploaded_at: string;
}

const statusLabels: Record<string, string> = {
  draft: "초안",
  signed: "서명완료",
  confirmed: "확정",
  cancelled: "취소",
};

export default function ContractDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [contract, setContract] = useState<Contract | null>(null);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.allSettled([
      contractsApi.get(id),
      contractsApi.listAttachments(id),
    ]).then(([contractRes, attachRes]) => {
      if (contractRes.status === "fulfilled") {
        const data = contractRes.value.data?.data ?? contractRes.value.data;
        setContract(data);
        setNewStatus(data?.contract_status ?? "draft");
      }
      if (attachRes.status === "fulfilled") {
        const data = attachRes.value.data;
        setAttachments(Array.isArray(data) ? data : data?.data ?? []);
      }
    }).finally(() => setLoading(false));
  }, [id]);

  async function handleStatusUpdate() {
    if (!contract) return;
    setSaving(true);
    try {
      await contractsApi.update(id, { contract_status: newStatus });
      setContract((prev) => prev ? { ...prev, contract_status: newStatus } : prev);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner size="lg" text="계약 정보 로딩 중..." />;
  if (!contract) {
    return (
      <div className="py-16 text-center text-slate-400">
        계약 정보를 찾을 수 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/arki/contracts")}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" />
        계약 목록으로
      </button>

      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-900">
          {contract.contract_number ?? "계약번호 미지정"}
        </h2>
        <Badge status={contract.contract_status}>
          {statusLabels[contract.contract_status] ?? contract.contract_status}
        </Badge>
        <Badge variant={contract.delivery_required ? "blue" : "gray"}>
          배송 {contract.delivery_required ? "필요" : "불필요"}
        </Badge>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">계약 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            { label: "계약번호", value: contract.contract_number ?? "—" },
            { label: "고객 ID", value: contract.customer_name ?? contract.customer_id },
            { label: "계약일", value: dayjs(contract.contract_date).format("YYYY-MM-DD") },
            { label: "계약금액", value: `${Number(contract.contract_amount).toLocaleString()}원` },
            { label: "계약금", value: contract.deposit_amount ? `${Number(contract.deposit_amount).toLocaleString()}원` : "—" },
            { label: "비고", value: contract.remarks ?? "—" },
            { label: "등록일", value: dayjs(contract.created_at).format("YYYY-MM-DD HH:mm") },
            { label: "수정일", value: dayjs(contract.updated_at).format("YYYY-MM-DD HH:mm") },
          ].map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">
                {f.label}
              </dt>
              <dd className="mt-1 text-sm text-slate-900">{f.value}</dd>
            </div>
          ))}
        </dl>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">상태 변경</h3>
        <div className="flex items-center gap-3">
          <Select
            options={[
              { value: "draft", label: "초안" },
              { value: "signed", label: "서명완료" },
              { value: "confirmed", label: "확정" },
              { value: "cancelled", label: "취소" },
            ]}
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            className="w-40"
          />
          <Button
            size="sm"
            onClick={handleStatusUpdate}
            loading={saving}
            disabled={newStatus === contract.contract_status}
          >
            변경 저장
          </Button>
        </div>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 flex items-center gap-2 font-semibold text-slate-900">
          <Paperclip className="h-4 w-4" />
          첨부 파일
        </h3>
        {attachments.length === 0 ? (
          <p className="text-sm text-slate-400">첨부 파일이 없습니다.</p>
        ) : (
          <ul className="space-y-2">
            {attachments.map((a) => (
              <li key={a.id} className="flex items-center gap-3">
                <Paperclip className="h-4 w-4 text-slate-400" />
                <a
                  href={a.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:underline"
                >
                  {a.file_name}
                </a>
                <span className="text-xs text-slate-400">
                  {dayjs(a.uploaded_at).format("YYYY-MM-DD")}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
