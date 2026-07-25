// Gestão simples do token JWT no cliente (localStorage). Suficiente para o
// walking skeleton; evoluir para cookies httpOnly/refresh quando endurecer.
const ACCESS_KEY = "beautyos.access";

export function saveToken(token: string): void {
  localStorage.setItem(ACCESS_KEY, token);
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function clearToken(): void {
  localStorage.removeItem(ACCESS_KEY);
}
