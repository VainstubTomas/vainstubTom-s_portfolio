/** Tecnologías del bloque principal (lectura rápida). */
export const MAIN_STACK = ["TypeScript", "React", "GCP", "Python", "Docker"] as const;

/** Resto del ecosistema en la cinta (sin duplicar el main stack). */
export const MARQUEE_STACK = [
    "Node.js",
    "MongoDB",
    "AWS",
    "Git",
    "Go",
    "Electron",
    "CouchBase",
    "Express",
    "Arduino",
    "n8n",
    "JavaScript",
    "FastAPI",
    "CI/CD",
] as const;

export type StackName = (typeof MAIN_STACK)[number] | (typeof MARQUEE_STACK)[number];
