import type { Lang } from '../i18n'
import { T } from '../i18n'
import type { SubTool } from '../types/pricing'
import { PERIODS, calcSubCost } from '../lib/cost'
import { DualCell } from './DualCell'
import { fmtUSD, fmtJPY } from '../lib/cost'

const GROUP_COLORS: Record<string, string> = {
  'GitHub Copilot':   '#238636',
  'Cursor':           '#7c3aed',
  'Claude Code':      '#c084fc',
  'Windsurf':         '#0ea5e9',
  'OpenAI Codex':     '#10b981',
  'JetBrains AI':     '#f472b6',
  'Junie (JetBrains)':'#ec4899',
  'Google One AI':    '#4285f4',
  'Antigravity':      '#818cf8',
}

interface Props {
  lang: Lang
  tools: SubTool[]
  jpyRate: number
}

export function SubTable({ lang, tools, jpyRate }: Props) {
  let lastGroup = ''

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>{T.colTool[lang]}</th>
            {[T.col1h, T.col8h, T.col24h, T.col7d, T.col30d, T.col4mo, T.col12mo].map((col, i) => (
              <th key={i}>{col[lang]}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tools.map((t, idx) => {
            const isNewGroup = t.group !== lastGroup
            lastGroup = t.group
            const color = GROUP_COLORS[t.group] ?? '#aaa'
            const note = lang === 'ja' ? t.note_ja : t.note_en

            const mJPY = Math.round(t.monthly * jpyRate).toLocaleString('ja-JP')
            const mStr = t.monthly === 0 ? 'FREE' : `${fmtUSD(t.monthly)}/mo (¥${mJPY})`
            const aStr = t.annual != null
              ? ` | ${T.annualLabel[lang]} ${fmtUSD(t.annual)}/mo (¥${Math.round(t.annual * jpyRate).toLocaleString('ja-JP')})`
              : ''

            return [
              isNewGroup && (
                <tr key={`grp-${idx}`} className="group-header">
                  <td
                    colSpan={8}
                    style={{ color, borderLeft: `3px solid ${color}`, paddingLeft: '11px' }}
                  >
                    ● {t.group}
                  </td>
                </tr>
              ),
              <tr key={`row-${idx}`}>
                <td>
                  <div className="model-cell">
                    <span className="model-name">{t.group} — {t.name}</span>
                    <span className="model-sub">{mStr}{aStr}</span>
                    <span className={`model-tag ${t.cls}`}>{t.tag}</span>
                    <span style={{ fontSize: '10px', color: 'var(--txt3)' }}>{note}</span>
                  </div>
                </td>
                {PERIODS.map((p, pi) => {
                  const usd = calcSubCost(t.monthly, t.annual, p.hours)
                  const annualNote =
                    p.hours >= 8760 && t.annual != null && t.annual < t.monthly * 12
                      ? `${T.annualLabel[lang]} ${fmtUSD(t.annual)}/yr (¥${fmtJPY(t.annual, jpyRate).replace('¥', '')})`
                      : null
                  return (
                    <td key={pi}>
                      <DualCell usd={usd} jpyRate={jpyRate} annualNote={annualNote} />
                    </td>
                  )
                })}
              </tr>,
            ]
          })}
        </tbody>
      </table>
    </div>
  )
}
