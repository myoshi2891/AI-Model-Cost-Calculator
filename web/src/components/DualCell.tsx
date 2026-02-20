import { colorIndex, fmtUSD, fmtJPY } from '../lib/cost'

interface Props {
  usd: number
  jpyRate: number
  annualNote?: string | null
}

export function DualCell({ usd, jpyRate, annualNote }: Props) {
  const n = colorIndex(usd)
  return (
    <div className="cost-wrap">
      <span className={`cost-usd cc-${n}`}>{fmtUSD(usd)}</span>
      <span className={`cost-jpy jpy-${n}`}>{fmtJPY(usd, jpyRate)}</span>
      {annualNote && <span className="sub-flat">{annualNote}</span>}
    </div>
  )
}
