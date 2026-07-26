"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import Nav from "@/app/components/Nav";
import { api, ApiError } from "@/lib/api";
import { getToken } from "@/lib/auth";

type Named = { id: string; name: string };
type Appointment = { id: string; starts_at: string; status: string };

export default function AgendaPage() {
  const router = useRouter();
  const [services, setServices] = useState<Named[]>([]);
  const [professionals, setProfessionals] = useState<Named[]>([]);
  const [customers, setCustomers] = useState<Named[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const [customerId, setCustomerId] = useState("");
  const [professionalId, setProfessionalId] = useState("");
  const [serviceId, setServiceId] = useState("");
  const [startsAt, setStartsAt] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      const [svc, prof, cust, appts] = await Promise.all([
        api.list<Named>("/services"),
        api.list<Named>("/professionals"),
        api.list<Named>("/customers"),
        api.list<Appointment>("/appointments"),
      ]);
      setServices(svc);
      setProfessionals(prof);
      setCustomers(cust);
      setAppointments(appts);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
        return;
      }
      setError(err instanceof Error ? err.message : "Erro ao carregar.");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    void load();
  }, [router, load]);

  async function book(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api.post("/appointments", {
        customer_id: customerId,
        professional_id: professionalId,
        service_id: serviceId,
        starts_at: new Date(startsAt).toISOString(),
      });
      setStartsAt("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao agendar.");
    }
  }

  if (loading) return <div className="container">Carregando…</div>;

  return (
    <div className="container">
      <Nav />
      <h1>Agenda</h1>
      {error && <p className="error">{error}</p>}

      <div className="card">
        <h2>Novo agendamento</h2>
        <form onSubmit={book}>
          <label>Cliente</label>
          <select value={customerId} onChange={(e) => setCustomerId(e.target.value)} required>
            <option value="">Selecione…</option>
            {customers.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <label>Profissional</label>
          <select value={professionalId} onChange={(e) => setProfessionalId(e.target.value)} required>
            <option value="">Selecione…</option>
            {professionals.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
          <label>Serviço</label>
          <select value={serviceId} onChange={(e) => setServiceId(e.target.value)} required>
            <option value="">Selecione…</option>
            {services.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <label>Início</label>
          <input type="datetime-local" value={startsAt} onChange={(e) => setStartsAt(e.target.value)} required />
          <button type="submit">Agendar</button>
        </form>
      </div>

      <div className="card">
        <h2>Agendamentos ({appointments.length})</h2>
        <ul>
          {appointments.map((a) => (
            <li key={a.id}>
              {new Date(a.starts_at).toLocaleString("pt-BR")} — {a.status}
            </li>
          ))}
          {appointments.length === 0 && <li className="muted">Nenhum agendamento.</li>}
        </ul>
      </div>
    </div>
  );
}
