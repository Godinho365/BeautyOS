"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import Nav from "@/app/components/Nav";
import { api, ApiError } from "@/lib/api";
import { getToken } from "@/lib/auth";

type Service = { id: string; name: string; duration_minutes: number; price_cents: number };
type Insights = {
  revenue_today_cents: number;
  appointments_today: number;
  low_stock_products: number;
  customers_total: number;
  suggestions: string[];
};

export default function DashboardPage() {
  const router = useRouter();
  const [services, setServices] = useState<Service[]>([]);
  const [insights, setInsights] = useState<Insights | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setError("");
    try {
      const [svc, ins] = await Promise.all([
        api.list<Service>("/services"),
        api.get<Insights>("/ai/insights"),
      ]);
      setServices(svc);
      setInsights(ins);
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

  if (loading) return <div className="container">Carregando…</div>;

  return (
    <div className="container">
      <Nav />
      <h1>Dashboard</h1>
      {error && <p className="error">{error}</p>}

      {insights && (
        <div className="card">
          <h2>Copilot — hoje</h2>
          <div className="row">
            <div className="card"><strong>R$ {(insights.revenue_today_cents / 100).toFixed(2)}</strong><br /><span className="muted">Receita</span></div>
            <div className="card"><strong>{insights.appointments_today}</strong><br /><span className="muted">Agendamentos</span></div>
            <div className="card"><strong>{insights.low_stock_products}</strong><br /><span className="muted">Estoque baixo</span></div>
            <div className="card"><strong>{insights.customers_total}</strong><br /><span className="muted">Clientes</span></div>
          </div>
          <ul>
            {insights.suggestions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </div>
      )}

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
    </div>
  );
}
