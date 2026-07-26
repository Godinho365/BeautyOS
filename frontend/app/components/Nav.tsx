"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { clearToken } from "@/lib/auth";

const LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/agenda", label: "Agenda" },
  { href: "/comandas", label: "Comandas" },
  { href: "/estoque", label: "Estoque" },
  { href: "/marketplace", label: "Marketplace" },
];

export default function Nav() {
  const pathname = usePathname();
  const router = useRouter();

  function logout() {
    clearToken();
    router.push("/login");
  }

  return (
    <div className="topbar">
      <nav style={{ display: "flex", gap: 16 }}>
        {LINKS.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            style={{ fontWeight: pathname === l.href ? 700 : 400 }}
          >
            {l.label}
          </Link>
        ))}
      </nav>
      <button className="linkbtn" onClick={logout}>
        Sair
      </button>
    </div>
  );
}
