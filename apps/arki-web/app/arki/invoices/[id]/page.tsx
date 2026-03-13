"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { invoicesApi } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import dayjs from "dayjs";

interface Invoice {
  id: string;
  invoice_number: string;
  po_id: string | null;
  supplier: string;
  invoice_date: string;
  due_date: string | null;
  total_amount: number;
  paid_amount: number | null;
  currency: string;
  payment_status: string;
  bank_info: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

const paymentLabels: Record<string, string> = {
  unpaid: "미결제",
  partially_paid: "부분결제",
  paid: "결제완료",
};

export default function InvoiceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [loading, setLoading] = useState(true);
  const [newStatus, setNewStatus] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    invoicesApi
      .get(id)
      .then((res) => {
        const data = res.data?.data ?? res.data;
        setInvoice(data);
        setNewStatus(data?.payment_status ?? "unpaid");
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  async function handleStatusUpdate() {
    if (!invoice) return;
    setSaving(true);
    try {
      await invoicesApi.update(id, { payment_status: newStatus });
      setInvoice((prev) => prev ? { ...prev, payment_status: newStatus } : prev);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner size="lg" text="인보이스 로딩 중..." />;
  if (!invoice) {
    return (
      <div className="py-16 text-center text-slate-400">
        인보이스를 찾을 수 없습니다.
      </div>
    );
  }

  const remaining = invoice.total_amount - (invoice.paid_amount ?? 0);

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/arki/invoices")}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" />
        인보이스 목록으로
      </button>

      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-900">{invoice.invoice_number}</h2>
        <Badge status={invoice.payment_status}>
          {paymentLabels[invoice.payment_status] ?? invoice.payment_status}
        </Badge>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">인보이스 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            { label: "인보이스번호", value: invoice.invoice_number },
            { label: "공급업체", value: invoice.supplier },
            { label: "발행일", value: dayjs(invoice.invoice_date).format("YYYY-MM-DD") },
            { label: "지급기한", value: invoice.due_date ? dayjs(invoice.due_date).format("YYYY-MM-DD") : "—" },
            { label: "총 금액", value: `${Number(invoice.total_amount).toLocaleString()} ${invoice.currency}` },
            { label: "결제 금액", value: invoice.paid_amount ? `${Number(invoice.paid_amount).toLocaleString()} ${invoice.currency}` : "—" },
            { label: "잔액", value: `${Number(remaining).toLocaleString()} ${invoice.currency}` },
            { label: "은행 정보", value: invoice.bank_info ?? "—" },
            { label: "비고", value: invoice.notes ?? "—" },
            { label: "등록일", value: dayjs(invoice.created_at).format("YYYY-MM-DD HH:mm") },
          ].map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">{f.label}</dt>
              <dd className="mt-1 text-sm text-slate-900">{f.value}</dd>
            </div>
          ))}
        </dl>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">결제 상태 변경</h3>
        <div className="flex items-center gap-3">
          <Select
            options={[
              { value: "unpaid", label: "미결제" },
              { value: "partially_paid", label: "부분결제" },
              { value: "paid", label: "결제완료" },
            ]}
            value={newStatus}
            onChange={(e) => setNewStatus(e.target.value)}
            className="w-40"
          />
          <Button
            size="sm"
            onClick={handleStatusUpdate}
            loading={saving}
            disabled={newStatus === invoice.payment_status}
          >
            변경 저장
          </Button>
        </div>
      </div>
    </div>
  );
}
