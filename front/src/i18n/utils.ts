import en from './en/en.json';
import es from './es/es.json';
import pr from './pr/pr.json';

export const languages = {
  en,
  es,
  pr
};

export const defaultLang = 'es';

export function useTranslations(lang: keyof typeof languages) {
  return function t(key: string): string {
    const translations = languages[lang] as Record<string, string>;
    return translations[key] || key;
  }
}

export function getLangFromUrl(url: URL) {
  const [, lang] = url.pathname.split('/');
  if (lang in languages) return lang as keyof typeof languages;
  return defaultLang;
}