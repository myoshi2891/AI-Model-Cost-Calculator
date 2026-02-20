import type { Lang } from '../i18n'
import { T } from '../i18n'

interface Props {
  lang: Lang
  jpyRate: number
}

export function MathSection({ lang, jpyRate }: Props) {
  const rateRounded = jpyRate.toFixed(2)

  return (
    <div className="math-section section" style={{ marginTop: '36px' }}>
      <div className="math-title">{T.mathTitle[lang]}</div>
      <div className="math-grid">

        {/* カード1: API コスト基本計算式 */}
        <div className="math-card">
          <h4>{lang === 'ja' ? '📐 API コスト基本計算式' : '📐 API Cost Formula'}</h4>
          <div className="formula">
            <span className="comment">
              {lang === 'ja' ? '// 1時間あたりのコスト (USD)' : '// Hourly cost (USD)'}
            </span>{'\n'}
            <span className="var">cost_usd/h</span>
            {' '}<span className="op">=</span>{'\n'}
            {'  '}(<span className="var">in_tok</span>{'  '}<span className="op">÷</span>{' '}
            <span className="num">1,000,000</span>) <span className="op">×</span>{' '}
            <span className="var">price_in</span>{'\n'}
            + (<span className="var">out_tok</span> <span className="op">÷</span>{' '}
            <span className="num">1,000,000</span>) <span className="op">×</span>{' '}
            <span className="var">price_out</span>{'\n\n'}
            <span className="comment">
              {lang === 'ja'
                ? `// 日本円換算 (レート: ${rateRounded} JPY/USD)`
                : `// JPY conversion (rate: ${rateRounded} JPY/USD)`}
            </span>{'\n'}
            <span className="var">cost_jpy</span>{' '}<span className="op">=</span>{' '}
            <span className="var">cost_usd</span>{' '}<span className="op">×</span>{' '}
            <span className="num">{rateRounded}</span>{'\n\n'}
            <span className="comment">
              {lang === 'ja' ? '// 各期間の換算 (hours)' : '// Period hours'}
            </span>{'\n'}
            1h<span className="op">=</span><span className="num">1</span>{' '}
            8h<span className="op">=</span><span className="num">8</span>{' '}
            24h<span className="op">=</span><span className="num">24</span>{' '}
            7d<span className="op">=</span><span className="num">168</span>{'\n'}
            30d<span className="op">=</span><span className="num">720</span>{' '}
            4mo<span className="op">=</span><span className="num">2,920</span>{' '}
            12mo<span className="op">=</span><span className="num">8,760</span>
          </div>
        </div>

        {/* カード2: シナリオ別トークン量 */}
        <div className="math-card">
          <h4>
            {lang === 'ja'
              ? '📊 各シナリオの前提トークン量'
              : '📊 Scenario Token Assumptions'}
          </h4>
          <div className="formula">
            <span className="comment">
              {lang === 'ja' ? '// Nano — Q&A・単純分類' : '// Nano — Q&A / simple tasks'}
            </span>{'\n'}
            IN<span className="op">=</span><span className="num">10,000</span>
            {'  '}OUT<span className="op">=</span><span className="num">3,000</span>{'\n\n'}
            <span className="comment">
              {lang === 'ja' ? '// Light — コード補完サポート' : '// Light — code completion'}
            </span>{'\n'}
            IN<span className="op">=</span><span className="num">50,000</span>
            {'  '}OUT<span className="op">=</span><span className="num">15,000</span>{'\n\n'}
            <span className="comment">
              {lang === 'ja' ? '// Standard — 積極的AI活用' : '// Standard — active AI usage'}
            </span>{'\n'}
            IN<span className="op">=</span><span className="num">150,000</span>
            {'  '}OUT<span className="op">=</span><span className="num">50,000</span>{'\n\n'}
            <span className="comment">
              {lang === 'ja' ? '// Heavy — 集中開発セッション' : '// Heavy — intensive dev'}
            </span>{'\n'}
            IN<span className="op">=</span><span className="num">400,000</span>
            {'  '}OUT<span className="op">=</span><span className="num">150,000</span>{'\n\n'}
            <span className="comment">
              {lang === 'ja' ? '// Agentic — 自律エージェント' : '// Agentic — autonomous AI'}
            </span>{'\n'}
            IN<span className="op">=</span><span className="num">1,000,000</span>
            {'  '}OUT<span className="op">=</span><span className="num">400,000</span>
          </div>
        </div>

        {/* カード3: 為替レート */}
        <div className="math-card">
          <h4>{lang === 'ja' ? '💱 USD/JPY 換算レート根拠' : '💱 USD/JPY Exchange Rate'}</h4>
          <div className="formula">
            <span className="comment">
              {lang === 'ja' ? '// Frankfurter API (ECB) 採用レート' : '// Frankfurter API (ECB) rate'}
            </span>{'\n'}
            <span className="var">1 USD</span>{' '}<span className="op">=</span>{' '}
            <span className="num">{rateRounded}</span> JPY{'\n\n'}
            <span className="comment">
              {lang === 'ja' ? '// 参考: レート情報源' : '// Reference sources'}
            </span>{'\n'}
            Frankfurter.app (ECB){'\n'}
            FRED: fred.stlouisfed.org{'\n'}
            Trading Economics{'\n\n'}
            <span className="comment">
              {lang === 'ja' ? '// ⚠ 為替は変動します' : '// ⚠ Rates fluctuate'}
            </span>
          </div>
        </div>

        {/* カード4: Vertex AI vs Google AI Studio */}
        <div className="math-card">
          <h4>
            {lang === 'ja'
              ? '🔷 Vertex AI vs Google AI Studio'
              : '🔷 Vertex AI vs Google AI Studio'}
          </h4>
          <div className="formula">
            <span className="comment">
              {lang === 'ja'
                ? '// 料金は同一 (2026年2月時点)'
                : '// Same pricing (as of Feb 2026)'}
            </span>{'\n'}
            <span className="var">Gemini 2.5 Pro</span>{'\n'}
            {'  '}IN <span className="op">=</span> $<span className="num">1.25</span>/1M (≤200K){'\n'}
            {'  '}IN <span className="op">=</span> $<span className="num">2.50</span>/1M (&gt;200K){'\n'}
            {'  '}OUT<span className="op">=</span> $<span className="num">10.00</span>/1M{'\n\n'}
            <span className="comment">
              {lang === 'ja' ? '// Vertex AI 固有の付加価値' : '// Vertex AI exclusive value'}
            </span>{'\n'}
            <span className="op">+</span> Enterprise SLA (99.9%){'\n'}
            <span className="op">+</span> VPC Service Controls{'\n'}
            <span className="op">+</span> Customer Encryption Keys{'\n'}
            <span className="op">+</span> GCP IAM / Model Garden
          </div>
        </div>

      </div>
    </div>
  )
}
