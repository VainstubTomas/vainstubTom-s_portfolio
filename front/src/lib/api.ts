export type Project = {
    id: number;
    title_es: string;
    title_en: string;
    title_pr: string;
    description_es: string;
    description_en: string;
    description_pr: string;
    link: string | null;
    github: string | null;
    image: string | null;
    tags: string[];
};

const API_URL = import.meta.env.PUBLIC_API_URL?.replace(/\/$/, "");

const TIMEOUT_MS = 90_000; // cold start de Render (~1 min)
const MAX_ATTEMPTS = 3;
const RETRY_DELAY_MS = 2_000;

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function apiFetch(path: string): Promise<Response> {
    if (!API_URL) {
        throw new Error("Falta PUBLIC_API_URL (front/.env o variable de Netlify).");
    }

    let lastError: unknown;
    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
        try {
        const res = await fetch(`${API_URL}${path}`, {
            signal: AbortSignal.timeout(TIMEOUT_MS),
        });
        if (!res.ok) {
            throw new Error(`La API respondió ${res.status} en ${path}`);
        }
        return res;
        } catch (err) {
        lastError = err;
        if (attempt < MAX_ATTEMPTS) await sleep(RETRY_DELAY_MS);
        }
    }
    throw new Error(
        `No se pudo leer ${path} tras ${MAX_ATTEMPTS} intentos: ${lastError}`,
    );
}

// Se guarda la promesa a nivel de módulo: las 3 páginas (es, en, pr)
// comparten una sola llamada durante el build.
let projectsPromise: Promise<Project[]> | undefined;

export function getProjects(): Promise<Project[]> {
    projectsPromise ??= apiFetch("/projects/").then((res) => res.json());
    return projectsPromise;
}