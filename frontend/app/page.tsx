"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { api, ApiError } from "@/lib/api";
import { clearToken, getToken } from "@/lib/auth";

type Service = { id: string; name: string; duration_minutes: number; price_cents: number };
type Appointment = { id: string; starts_at: string; status: string };

export default function DashboardPage() {
  const router = useRouter();
  const [services, setServices] = useState<Service[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // formulário de novo serviço
  const [name, setName] = useState("");
  const [duration, setDuration] = useState(30);
  const [price, setPrice] = useState(5000);

  const load = useCallback(async () => {
    setError("");
    try {
      const [svc, appts] = await Promise.all([
        api.get<Service[]>("/services"),
        api.get<Appointment[]>("/appointments"),
      ]);
      setServices(svc);
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

  async function createService(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post("/services", {
        name,
        duration_minutes: duration,
        price_cents: price,
      });
      setName("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao criar serviço.");
    }
  }

  function logout() {
    clearToken();
    router.push("/login");
  }

  if (loading) return <div className="container">Carregando…</div>;

  return (
    <div className="container">
      <div className="topbar">
        <h1>Painel BeautyOS</h1>
        <button className="linkbtn" onClick={logout}>
          Sair
        </button>
      </div>
      {error && <p className="error">{error}</p>}

      <div className="row">
        <div className="card">
          <h2>Serviços ({services.length})</h2>
          <ul>
            {services.map((s) => (
              <li key={s.id}>
                {s.name} — {s.duration_minutes}min — R$ {(s.price_cents / 100).toFixed(2)}
              </li>
            ))}
            {services.length === 0 && <li className="muted">Nenhum serviço.</li>}
          </ul>
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

      <div className="card">
        <h2>Novo serviço</h2>
        <form onSubmit={createService}>
          <label htmlFor="name">Nome</label>
          <input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
          <div className="row">
            <div style={{ flex: 1 }}>
              <label htmlFor="dur">Duração (min)</label>
              <input
                id="dur"
                type="number"
                min={1}
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
              />
            </div>
            <div style={{ flex: 1 }}>
              <label htmlFor="price">Preço (centavos)</label>
              <input
                id="price"
                type="number"
                min={0}
                value={price}
                onChange={(e) => setPrice(Number(e.target.value))}
              />
            </div>
          </div>
          <button type="submit">Criar serviço</button>
        </form>
      </div>
    </div>
  );
}
