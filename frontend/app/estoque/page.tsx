"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import Nav from "@/app/components/Nav";
import { api, ApiError } from "@/lib/api";
import { getToken } from "@/lib/auth";

type Product = { id: string; name: string; sku: string; quantity: number };

export default function EstoquePage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const [name, setName] = useState("");
  const [sku, setSku] = useState("");

  const load = useCallback(async () => {
    setError("");
    try {
      setProducts(await api.list<Product>("/products"));
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

  async function run(fn: () => Promise<unknown>) {
    setError("");
    try {
      await fn();
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro.");
    }
  }

  const createProduct = (e: React.FormEvent) => {
    e.preventDefault();
    void run(async () => {
      await api.post("/products", { name, sku });
      setName("");
      setSku("");
    });
  };

  const adjust = (id: string, delta: number) =>
    void run(() => api.post(`/products/${id}/adjust`, { delta, reason: "ajuste manual" }));

  if (loading) return <div className="container">Carregando…</div>;

  return (
    <div className="container">
      <Nav />
      <h1>Estoque</h1>
      {error && <p className="error">{error}</p>}

      <div className="card">
        <h2>Novo produto</h2>
        <form onSubmit={createProduct}>
          <label>Nome</label>
          <input value={name} onChange={(e) => setName(e.target.value)} required />
          <label>SKU</label>
          <input value={sku} onChange={(e) => setSku(e.target.value)} />
          <button type="submit">Criar produto</button>
        </form>
      </div>

      <div className="card">
        <h2>Produtos ({products.length})</h2>
        <ul>
          {products.map((p) => (
            <li key={p.id} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ flex: 1 }}>{p.name} {p.sku && `(${p.sku})`} — saldo: <strong>{p.quantity}</strong></span>
              <button className="linkbtn" onClick={() => adjust(p.id, 1)}>+1</button>
              <button className="linkbtn" onClick={() => adjust(p.id, -1)}>−1</button>
            </li>
          ))}
          {products.length === 0 && <li className="muted">Nenhum produto.</li>}
        </ul>
      </div>
    </div>
  );
}
