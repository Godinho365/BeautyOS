"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import Nav from "@/app/components/Nav";
import { api, ApiError } from "@/lib/api";
import { getToken } from "@/lib/auth";

type Profile = { slug: string; display_name: string; bio: string; is_published: boolean };

export default function MarketplacePage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");
  const [loading, setLoading] = useState(true);

  const [slug, setSlug] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [bio, setBio] = useState("");
  const [published, setPublished] = useState(false);

  const load = useCallback(async () => {
    try {
      const p = await api.get<Profile>("/marketplace/profile");
      setSlug(p.slug);
      setDisplayName(p.display_name);
      setBio(p.bio);
      setPublished(p.is_published);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) return router.push("/login");
      // 404 = ainda sem perfil; formulário segue vazio para criar.
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    if (!getToken()) return router.push("/login");
    void load();
  }, [router, load]);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setOk("");
    try {
      await api.put("/marketplace/profile", {
        slug, display_name: displayName, bio, is_published: published,
      });
      setOk("Perfil salvo.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao salvar.");
    }
  }

  if (loading) return <div className="container">Carregando…</div>;

  return (
    <div className="container">
      <Nav />
      <h1>Marketplace</h1>
      {error && <p className="error">{error}</p>}
      {ok && <p style={{ color: "#2b8a3e" }}>{ok}</p>}

      <div className="card">
        <h2>Perfil público</h2>
        <form onSubmit={save}>
          <label>Slug (URL pública)</label>
          <input value={slug} onChange={(e) => setSlug(e.target.value)} placeholder="meu-salao" required />
          <label>Nome de exibição</label>
          <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} required />
          <label>Bio</label>
          <input value={bio} onChange={(e) => setBio(e.target.value)} />
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              style={{ width: "auto" }}
              checked={published}
              onChange={(e) => setPublished(e.target.checked)}
            />
            Publicado no marketplace
          </label>
          <button type="submit">Salvar</button>
        </form>
        {published && slug && (
          <p className="muted" style={{ marginTop: 12 }}>
            Página pública: <Link href={`/descobrir/${slug}`}>/descobrir/{slug}</Link>
          </p>
        )}
      </div>
    </div>
  );
}
