import { useState } from 'react'
import type { Lang } from '../i18n'
import { T } from '../i18n'
import type { ApiModel } from '../types/pricing'
import { PERIODS, calcApiCost } from '../lib/cost'
import { DualCell } from './DualCell'

const PROVIDER_COLORS: Record<string, string> = {
  'OpenAI':    '#10b981',
  'Anthropic': '#c084fc',
  'Google AI': '#3b82f6',
  'Vertex AI': '#7dd3fc',
  'xAI':       '#94a3b8',
  'DeepSeek':  '#22d3ee',
  'AWS':       '#facc15',
}

interface Props {
  lang: Lang
  models: ApiModel[]
  inputTokens: number
  outputTokens: number
  jpyRate: number
}

export function ApiTable({ lang, models, inputTokens, outputTokens, jpyRate }: Props) {
  const [sortCol, setSortCol] = useState<number | null>(null)
  const [sortDir, setSortDir] = useState(1)

  const rows = models.map(m => ({
    ...m,
    costs: PERIODS.map(p => calcApiCost(m.price_in, m.price_out, inputTokens, outputTokens, p.hours)),
  }))

  if (sortCol !== null) {
    rows.sort((a, b) => sortDir * (a.costs[sortCol] - b.costs[sortCol]))
  }

  const min30 = Math.min(...rows.map(r => r.costs[4]))

  const toggleSort = (colIdx: number) => {
    if (sortCol === colIdx) {
      setSortDir(d => d * -1)
    } else {
      setSortCol(colIdx)
      setSortDir(1)
    }
  }

  const colKeys = [T.col1h, T.col8h, T.col24h, T.col7d, T.col30d, T.col4mo, T.col12mo] as const

  let lastProvider = ''

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>{T.colModel[lang]}</th>
            {colKeys.map((col, i) => (
              <th
                key={i}
                onClick={() => toggleSort(i)}
                style={{ cursor: 'pointer' }}
                title={lang === 'ja' ? 'クリックでソート' : 'Click to sort'}
              >
                {col[lang]}
                {sortCol === i ? (sortDir > 0 ? ' ▲' : ' ▼') : ''}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((m, idx) => {
            const isNewProvider = m.provider !== lastProvider
            lastProvider = m.provider
            const isCheap = m.costs[4] === min30
            const sub = lang === 'ja' ? m.sub_ja : m.sub_en
            const color = PROVIDER_COLORS[m.provider] ?? '#aaa'

            return [
              isNewProvider && (
                <tr key={`grp-${idx}`} className="group-header">
                  <td
                    colSpan={8}
                    style={{ color, borderLeft: `3px solid ${color}`, paddingLeft: '11px' }}
                  >
                    ● {m.provider}
                  </td>
                </tr>
              ),
              <tr key={`row-${idx}`} className={isCheap ? 'cheapest-row' : ''}>
                <td>
                  <div className="model-cell">
                    <span className="model-name">
                      {m.name}
                      {isCheap && <span className="cheapest-badge">{T.cheapestBadge[lang]}</span>}
                    </span>
                    <span className="model-sub">
                      ${m.price_in} in / ${m.price_out} out /1M &nbsp;|&nbsp;
                      ¥{Math.round(m.price_in * jpyRate)} / ¥{Math.round(m.price_out * jpyRate)}
                    </span>
                    <span className={`model-tag ${m.cls}`}>{m.tag}</span>
                    <span style={{ fontSize: '10px', color: 'var(--txt3)' }}>{sub}</span>
                  </div>
                </td>
                {m.costs.map((cost, ci) => (
                  <td key={ci}>
                    <DualCell usd={cost} jpyRate={jpyRate} />
                  </td>
                ))}
              </tr>,
            ]
          })}
        </tbody>
      </table>
    </div>
  )
}
