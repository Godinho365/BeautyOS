"use client";

import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { api } from "@/lib/api";

type Named = { id: string; name: string };
type Service = Named & { duration_minutes: number; price_cents: number };
type Detail = {
  slug: string; display_name: string; bio: string;
  services: Service[]; professionals: Named[];
};

const brl = (c: number) => `R$ ${(c / 100).toFixed(2)}`;

export default function PublicCompanyPage() {
  const { slug } = useParams<{ slug: string }>();
  const [detail, setDetail] = useState<Detail | null>(null);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [loading, setLoading] = useState(true);

  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [professionalId, setProfessionalId] = useState("");
  const [serviceId, setServiceId] = useState("");
  const [startsAt, setStartsAt] = useState("");

  const load = useCallback(async () => {
    try {
      setDetail(await api.get<Detail>(`/marketplace/companies/${slug}`));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Empresa não encontrada.");
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => { void load(); }, [load]);

  async function book(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setOk("");
    try {
      await api.post(`/marketplace/companies/${slug}/book`, {
        customer_name: name, phone,
        professional_id: professionalId, service_id: serviceId,
        starts_at: new Date(startsAt).toISOString(),
      });
      setOk("Agendamento confirmado! Você receberá a confirmação.");
      setName(""); setPhone(""); setStartsAt("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível agendar.");
    }
  }

  if (loading) return <div className="container">Carregando…</div>;
  if (!detail) return <div className="container"><p className="error">{error}</p></div>;

  return (
    <div className="container" style={{ maxWidth: 640 }}>
      <h1 style={{ textTransform: "none" }}>{detail.display_name}</h1>
      {detail.bio && <p className="muted">{detail.bio}</p>}

      <div className="card">
        <h2>Serviços</h2>
        <ul>
          {detail.services.map((s) => (
            <li key={s.id}>{s.name} — {s.duration_minutes}min — {brl(s.price_cents)}</li>
          ))}
        </ul>
      </div>

      <div className="card">
        <h2>Agendar</h2>
        {error && <p className="error">{error}</p>}
        {ok && <p style={{ color: "#2b8a3e" }}>{ok}</p>}
        <form onSubmit={book}>
          <label>Seu nome</label>
          <input value={name} onChange={(e) => setName(e.target.value)} required />
          <label>Telefone</label>
          <input value={phone} onChange={(e) => setPhone(e.target.value)} />
          <label>Profissional</label>
          <select value={professionalId} onChange={(e) => setProfessionalId(e.target.value)} required>
            <option value="">Selecione…</option>
            {detail.professionals.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <label>Serviço</label>
          <select value={serviceId} onChange={(e) => setServiceId(e.target.value)} required>
            <option value="">Selecione…</option>
            {detail.services.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <label>Data e hora</label>
          <input type="datetime-local" value={startsAt} onChange={(e) => setStartsAt(e.target.value)} required />
          <button type="submit">Confirmar agendamento</button>
        </form>
      </div>
    </div>
  );
}
