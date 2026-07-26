"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";

type Company = { slug: string; display_name: string; bio: string };

export default function DescobrirPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Endpoint público (sem autenticação); retorna array simples.
    api.get<Company[]>("/marketplace/companies")
      .then(setCompanies)
      .catch((e) => setError(e instanceof Error ? e.message : "Erro."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="container">Carregando…</div>;

  return (
    <div className="container">
      <h1>Descobrir salões</h1>
      {error && <p className="error">{error}</p>}
      <div className="row">
        {companies.map((c) => (
          <div className="card" key={c.slug}>
            <h2 style={{ textTransform: "none" }}>{c.display_name}</h2>
            {c.bio && <p className="muted">{c.bio}</p>}
            <Link href={`/descobrir/${c.slug}`}>Ver e agendar →</Link>
          </div>
        ))}
        {companies.length === 0 && <p className="muted">Nenhum salão publicado ainda.</p>}
      </div>
    </div>
  );
}
