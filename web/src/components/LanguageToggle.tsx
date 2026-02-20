import type { Lang } from '../i18n'

interface Props {
  lang: Lang
  onToggle: (lang: Lang) => void
}

export function LanguageToggle({ lang, onToggle }: Props) {
  return (
    <div className="lang-toggle">
      <button
        className={`lang-btn ja${lang === 'ja' ? ' active' : ''}`}
        onClick={() => onToggle('ja')}
      >
        JA
      </button>
      <button
        className={`lang-btn en${lang === 'en' ? ' active' : ''}`}
        onClick={() => onToggle('en')}
      >
        EN
      </button>
    </div>
  )
}
