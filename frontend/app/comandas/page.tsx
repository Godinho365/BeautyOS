"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import Nav from "@/app/components/Nav";
import { api, ApiError } from "@/lib/api";
import { getToken } from "@/lib/auth";

type Named = { id: string; name: string };
type Item = { id: string; description: string; quantity: number; unit_price_cents: number; subtotal_cents: number };
type Payment = { id: string; amount_cents: number; method: string };
type Ticket = {
  id: string; customer_id: string; status: string; total_cents: number;
  paid_cents: number; items: Item[]; payments: Payment[];
};

const brl = (c: number) => `R$ ${(c / 100).toFixed(2)}`;

export default function ComandasPage() {
  const router = useRouter();
  const [customers, setCustomers] = useState<Named[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [selected, setSelected] = useState<Ticket | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const [customerId, setCustomerId] = useState("");
  const [desc, setDesc] = useState("");
  const [price, setPrice] = useState(5000);
  const [qty, setQty] = useState(1);
  const [payAmount, setPayAmount] = useState(0);

  const load = useCallback(async () => {
    setError("");
    try {
      const [cust, tks] = await Promise.all([
        api.list<Named>("/customers"),
        api.list<Ticket>("/tickets"),
      ]);
      setCustomers(cust);
      setTickets(tks);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return router.push("/login");
      setError(err instanceof Error ? err.message : "Erro ao carregar.");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    if (!getToken()) return router.push("/login");
    void load();
  }, [router, load]);

  async function refreshSelected(id: string) {
    setSelected(await api.get<Ticket>(`/tickets/${id}`));
    await load();
  }

  async function action<T>(fn: () => Promise<T>) {
    setError("");
    try {
      await fn();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro.");
    }
  }

  const openTicket = (e: React.FormEvent) => {
    e.preventDefault();
    void action(async () => {
      const t = await api.post<Ticket>("/tickets", { customer_id: customerId });
      await load();
      await refreshSelected(t.id);
    });
  };

  const addItem = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected) return;
    void action(async () => {
      await api.post(`/tickets/${selected.id}/items`, {
        description: desc, unit_price_cents: price, quantity: qty,
      });
      setDesc("");
      await refreshSelected(selected.id);
    });
  };

  const pay = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selected) return;
    void action(async () => {
      await api.post(`/tickets/${selected.id}/payments`, { amount_cents: payAmount });
      await refreshSelected(selected.id);
    });
  };

  const close = () => {
    if (!selected) return;
    void action(async () => {
      await api.post(`/tickets/${selected.id}/close`, {});
      await refreshSelected(selected.id);
    });
  };

  if (loading) return <div className="container">Carregando…</div>;

  return (
    <div className="container">
      <Nav />
      <h1>Comandas</h1>
      {error && <p className="error">{error}</p>}

      <div className="row">
        <div className="card">
          <h2>Abrir comanda</h2>
          <form onSubmit={openTicket}>
            <label>Cliente</label>
            <select value={customerId} onChange={(e) => setCustomerId(e.target.value)} required>
              <option value="">Selecione…</option>
              {customers.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <button type="submit">Abrir</button>
          </form>
        </div>

        <div className="card">
          <h2>Comandas ({tickets.length})</h2>
          <ul>
            {tickets.map((t) => (
              <li key={t.id}>
                <button className="linkbtn" onClick={() => void refreshSelected(t.id)}>
                  {t.id.slice(0, 8)} — {t.status} — {brl(t.total_cents)}
                </button>
              </li>
            ))}
            {tickets.length === 0 && <li className="muted">Nenhuma comanda.</li>}
          </ul>
        </div>
      </div>

      {selected && (
        <div className="card">
          <h2>Comanda {selected.id.slice(0, 8)} — {selected.status}</h2>
          <p className="muted">
            Total {brl(selected.total_cents)} · Pago {brl(selected.paid_cents)}
          </p>
          <ul>
            {selected.items.map((i) => (
              <li key={i.id}>{i.quantity}× {i.description} — {brl(i.subtotal_cents)}</li>
            ))}
            {selected.items.length === 0 && <li className="muted">Sem itens.</li>}
          </ul>

          {selected.status === "open" && (
            <>
              <form onSubmit={addItem}>
                <label>Item</label>
                <input value={desc} onChange={(e) => setDesc(e.target.value)} placeholder="Descrição" required />
                <div className="row">
                  <div style={{ flex: 1 }}>
                    <label>Preço (centavos)</label>
                    <input type="number" min={0} value={price} onChange={(e) => setPrice(Number(e.target.value))} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <label>Qtd</label>
                    <input type="number" min={1} value={qty} onChange={(e) => setQty(Number(e.target.value))} />
                  </div>
                </div>
                <button type="submit">Adicionar item</button>
              </form>

              <form onSubmit={pay}>
                <label>Pagamento (centavos)</label>
                <input type="number" min={1} value={payAmount} onChange={(e) => setPayAmount(Number(e.target.value))} />
                <button type="submit">Registrar pagamento</button>
              </form>

              <button onClick={close} style={{ background: "#2b8a3e" }}>Fechar comanda</button>
            </>
          )}
        </div>
      )}
    </div>
  );
}
