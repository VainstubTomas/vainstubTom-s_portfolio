export const NAV_LINKS = [
    { key: "nav.inicio", hash: "#inicio" },
    { key: "nav.exp", hash: "#experiencia" },
    { key: "nav.proyectos", page: "proyectos" },
    { key: "nav.contacto", hash: "#contacto" },
] as const;

export type NavLink = (typeof NAV_LINKS)[number];

export function navHref(lang: string, link: NavLink): string {
    if ("page" in link && link.page) return `/${lang}/${link.page}`;
    return `/${lang}/${link.hash}`;
}

export const EMAIL = "vainstubtomas@gmail.com";
