import type { APIRoute } from "astro";
import { apiFetch } from "../../lib/api";

// Endpoint estático: en el build descarga el CV de la API y lo publica
// como /files/resume.pdf. Si la API falla, el build falla.
export const GET: APIRoute = async () => {
  const res = await apiFetch("/resume");
  return new Response(await res.arrayBuffer(), {
    headers: { "Content-Type": "application/pdf" },
  });
};
