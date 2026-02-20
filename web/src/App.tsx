import { useState } from 'react'
import type { Lang } from './i18n'
import { T } from './i18n'
import type { PricingData } from './types/pricing'
import { SCENARIOS } from './components/ScenarioSelector'
import type { ScenarioKey } from './components/ScenarioSelector'
import { LanguageToggle } from './components/LanguageToggle'
import { Hero } from './components/Hero'
import { ScenarioSelector } from './components/ScenarioSelector'
import { ApiTable } from './components/ApiTable'
import { SubTable } from './components/SubTable'
import { MathSection } from './components/MathSection'
import { RefLinks } from './components/RefLinks'
import pricingJson from './data/pricing.json'

const pricing = pricingJson as PricingData

type TabKey = 'api' | 'sub'

export default function App() {
  const [lang, setLang] = useState<Lang>('ja')
  const [tab, setTab] = useState<TabKey>('api')
  const [scenario, setScenario] = useState<ScenarioKey>('standard')
  const [inputTokens, setInputTokens] = useState(SCENARIOS.standard.input)
  const [outputTokens, setOutputTokens] = useState(SCENARIOS.standard.output)

  const handleScenarioChange = (key: ScenarioKey, input: number, output: number) => {
    setScenario(key)
    setInputTokens(input)
    setOutputTokens(output)
  }

  const { jpy_rate, api_models, sub_tools } = pricing
  const apiCount = api_models.length
  const toolCount = sub_tools.length

  return (
    <>
      <LanguageToggle lang={lang} onToggle={setLang} />

      <Hero lang={lang} data={pricing} apiCount={apiCount} toolCount={toolCount} />

      <div className="container">
        <ScenarioSelector
          lang={lang}
          currentInput={inputTokens}
          currentOutput={outputTokens}
          scenario={scenario}
          onScenarioChange={handleScenarioChange}
        />

        <div className="section section-tabs">
          {/* 時間帯バッジ */}
          <div className="time-badges">
            <span className="time-badge tb-s">1h</span>
            <span className="time-badge tb-s">8h</span>
            <span className="time-badge tb-s">24h</span>
            <span className="time-badge tb-m">7d</span>
            <span className="time-badge tb-m">30d</span>
            <span className="time-badge tb-l">4mo</span>
            <span className="time-badge tb-l">12mo</span>
            <span className="cell-note-label">{T.cellNote[lang]}</span>
          </div>

          {/* タブ切り替え */}
          <div className="tabs">
            <button
              type="button"
              className={`tab-btn${tab === 'api' ? ' active' : ''}`}
              onClick={() => setTab('api')}
            >
              {T.tabApi[lang]}
            </button>
            <button
              type="button"
              className={`tab-btn${tab === 'sub' ? ' active' : ''}`}
              onClick={() => setTab('sub')}
            >
              {T.tabSub[lang]}
            </button>
          </div>

          {/* API テーブル */}
          {tab === 'api' && (
            <>
              <ApiTable
                lang={lang}
                models={api_models}
                inputTokens={inputTokens}
                outputTokens={outputTokens}
                jpyRate={jpy_rate}
              />
              <div
                className="note-box"
                dangerouslySetInnerHTML={{ __html: T.apiNote[lang] }}
              />
            </>
          )}

          {/* サブスク テーブル */}
          {tab === 'sub' && (
            <>
              <SubTable lang={lang} tools={sub_tools} jpyRate={jpy_rate} />
              <div
                className="note-box info"
                dangerouslySetInnerHTML={{ __html: T.subNote[lang] }}
              />
            </>
          )}
        </div>

        <MathSection lang={lang} jpyRate={jpy_rate} />

        <RefLinks lang={lang} />

        {/* 免責事項 */}
        <div
          className="disclaimer-box"
          dangerouslySetInnerHTML={{ __html: T.disclaimer[lang] }}
        />
      </div>

      <footer>
        <span>AI Cost Calculator v5 — {pricing.generated_at.slice(0, 10)} | USD + JPY (1 USD = {jpy_rate.toFixed(0)} JPY)</span>
        <span>cost = (IN/1M × price_in + OUT/1M × price_out) × hours × JPY_rate</span>
      </footer>
    </>
  )
}
