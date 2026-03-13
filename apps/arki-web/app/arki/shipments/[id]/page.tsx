"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { shipmentsApi } from "@/lib/api";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Select from "@/components/ui/Select";
import Spinner from "@/components/ui/Spinner";
import dayjs from "dayjs";

interface Shipment {
  id: string;
  bl_number: string;
  po_id: string | null;
  shipping_company: string;
  vessel_name: string | null;
  voyage_number: string | null;
  departure_port: string | null;
  arrival_port: string | null;
  departure_date: string | null;
  estimated_arrival_date: string | null;
  actual_arrival_date: string | null;
  total_cbm: number | null;
  total_weight_kg: number | null;
  shipment_status: string;
  customs_status: string;
  customs_declaration_number: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export default function ShipmentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;

  const [shipment, setShipment] = useState<Shipment | null>(null);
  const [loading, setLoading] = useState(true);
  const [newShipmentStatus, setNewShipmentStatus] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    shipmentsApi
      .get(id)
      .then((res) => {
        const data = res.data?.data ?? res.data;
        setShipment(data);
        setNewShipmentStatus(data?.shipment_status ?? "pending");
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [id]);

  async function handleStatusUpdate() {
    if (!shipment) return;
    setSaving(true);
    try {
      await shipmentsApi.update(id, { shipment_status: newShipmentStatus });
      setShipment((prev) => prev ? { ...prev, shipment_status: newShipmentStatus } : prev);
    } catch {
    } finally {
      setSaving(false);
    }
  }

  if (loading) return <Spinner size="lg" text="선적 정보 로딩 중..." />;
  if (!shipment) {
    return (
      <div className="py-16 text-center text-slate-400">
        선적 정보를 찾을 수 없습니다.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/arki/shipments")}
        className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
      >
        <ArrowLeft className="h-4 w-4" />
        선적 목록으로
      </button>

      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-900">{shipment.bl_number}</h2>
        <Badge status={shipment.shipment_status}>{shipment.shipment_status}</Badge>
        <Badge status={shipment.customs_status}>{shipment.customs_status}</Badge>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">선적 정보</h3>
        <dl className="grid grid-cols-2 gap-4">
          {[
            { label: "BL 번호", value: shipment.bl_number },
            { label: "선사", value: shipment.shipping_company },
            { label: "선박명", value: shipment.vessel_name ?? "—" },
            { label: "항차번호", value: shipment.voyage_number ?? "—" },
            { label: "출항항", value: shipment.departure_port ?? "—" },
            { label: "입항항", value: shipment.arrival_port ?? "—" },
            { label: "출항일", value: shipment.departure_date ? dayjs(shipment.departure_date).format("YYYY-MM-DD") : "—" },
            { label: "도착예정일", value: shipment.estimated_arrival_date ? dayjs(shipment.estimated_arrival_date).format("YYYY-MM-DD") : "—" },
            { label: "실제도착일", value: shipment.actual_arrival_date ? dayjs(shipment.actual_arrival_date).format("YYYY-MM-DD") : "—" },
            { label: "총 CBM", value: shipment.total_cbm ? `${shipment.total_cbm} CBM` : "—" },
            { label: "총 중량", value: shipment.total_weight_kg ? `${shipment.total_weight_kg} kg` : "—" },
            { label: "통관번호", value: shipment.customs_declaration_number ?? "—" },
            { label: "비고", value: shipment.notes ?? "—" },
            { label: "등록일", value: dayjs(shipment.created_at).format("YYYY-MM-DD HH:mm") },
          ].map((f) => (
            <div key={f.label}>
              <dt className="text-xs font-medium uppercase tracking-wider text-slate-400">{f.label}</dt>
              <dd className="mt-1 text-sm text-slate-900">{f.value}</dd>
            </div>
          ))}
        </dl>
      </div>

      <div className="rounded-xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h3 className="mb-4 font-semibold text-slate-900">선적 상태 변경</h3>
        <div className="flex items-center gap-3">
          <Select
            options={[
              { value: "pending", label: "대기" },
              { value: "in_transit", label: "운송중" },
              { value: "arrived", label: "도착" },
              { value: "completed", label: "완료" },
            ]}
            value={newShipmentStatus}
            onChange={(e) => setNewShipmentStatus(e.target.value)}
            className="w-40"
          />
          <Button
            size="sm"
            onClick={handleStatusUpdate}
            loading={saving}
            disabled={newShipmentStatus === shipment.shipment_status}
          >
            변경 저장
          </Button>
        </div>
      </div>
    </div>
  );
}
