import type { Lang } from '../i18n'
import type { PricingData } from '../types/pricing'
import { T } from '../i18n'

interface Props {
  lang: Lang
  data: PricingData
  apiCount: number
  toolCount: number
}

export function Hero({ lang, data, apiCount, toolCount }: Props) {
  const metaModels = T.metaModels[lang]
    .replace('{n}', String(apiCount))
    .replace('{m}', String(toolCount))

  const rateDateStr = T.rateDate[lang].replace(
    '{date}',
    data.jpy_rate_date === 'fallback' ? '–' : data.jpy_rate_date
  )

  const updatedDate = data.generated_at.slice(0, 10)

  return (
    <div className="hero">
      <div className="hero-inner">
        <div className="hero-eyebrow">{T.eyebrow[lang]}</div>
        <h1 dangerouslySetInnerHTML={{ __html: T.heroTitle[lang] }} />
        <p
          className="hero-desc"
          dangerouslySetInnerHTML={{ __html: T.heroDesc[lang] }}
        />
        <div className="hero-meta">
          <span>Step 1: {lang === 'ja' ? '使用シナリオを選択' : 'Select a usage scenario'}</span>
          <span>Step 2: {lang === 'ja' ? '必要に応じてカスタム設定' : 'Customize if needed'}</span>
          <span>Step 3: {lang === 'ja' ? '時間別コスト表を確認' : 'Review the cost table'}</span>
          <span>{metaModels}</span>
        </div>
        <div className="rate-badge">
          <span>{T.rateLabel[lang]}</span>
          <strong>1 USD = {data.jpy_rate.toFixed(2)} JPY</strong>
          <span style={{ opacity: 0.7, fontSize: '10px' }}>{rateDateStr}</span>
        </div>
        <div style={{ marginTop: '8px', fontSize: '11px', color: 'var(--txt3)', fontFamily: "'JetBrains Mono', monospace" }}>
          {T.updatedAt[lang]} {updatedDate}
        </div>
      </div>
    </div>
  )
}
