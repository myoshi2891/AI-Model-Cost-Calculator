import { useState } from 'react'
import type { Lang } from '../i18n'
import { T } from '../i18n'

export type ScenarioKey = 'nano' | 'light' | 'standard' | 'heavy' | 'agentic' | 'custom'

export const SCENARIOS: Record<ScenarioKey, { input: number; output: number; color: string }> = {
  nano:     { input: 10_000,    output: 3_000,   color: '#22d3ee' },
  light:    { input: 50_000,    output: 15_000,  color: '#4ade80' },
  standard: { input: 150_000,   output: 50_000,  color: '#60a5fa' },
  heavy:    { input: 400_000,   output: 150_000, color: '#f59e0b' },
  agentic:  { input: 1_000_000, output: 400_000, color: '#f87171' },
  custom:   { input: 150_000,   output: 50_000,  color: '#a78bfa' },
}

interface Props {
  lang: Lang
  currentInput: number
  currentOutput: number
  scenario: ScenarioKey
  onScenarioChange: (key: ScenarioKey, input: number, output: number) => void
}

export function ScenarioSelector({ lang, currentInput, currentOutput, scenario, onScenarioChange }: Props) {
  const [customInput, setCustomInput] = useState(150_000)
  const [customOutput, setCustomOutput] = useState(50_000)

  const selectScenario = (key: ScenarioKey) => {
    if (key === 'custom') {
      onScenarioChange('custom', customInput, customOutput)
    } else {
      const s = SCENARIOS[key]
      onScenarioChange(key, s.input, s.output)
    }
  }

  const updateCustomInput = (val: number) => {
    setCustomInput(val)
    if (scenario === 'custom') onScenarioChange('custom', val, customOutput)
  }

  const updateCustomOutput = (val: number) => {
    setCustomOutput(val)
    if (scenario === 'custom') onScenarioChange('custom', customInput, val)
  }

  const ratio = currentOutput > 0
    ? `${(currentInput / currentOutput).toFixed(1)}:1`
    : '–'
  const costPerH = `(IN/1M × $price_in + OUT/1M × $price_out) × h`

  return (
    <div className="panel">
      <div className="panel-title">{T.step1Title[lang]}</div>
      <div className="scenarios">
        {(['nano', 'light', 'standard', 'heavy', 'agentic', 'custom'] as ScenarioKey[]).map(key => {
          const s = SCENARIOS[key]
          const label = T[`sc_${key}` as keyof typeof T][lang] as string
          const rateText = key !== 'custom'
            ? `${(s.input / 1000).toFixed(0)}K / ${(s.output / 1000).toFixed(0)}K`
            : `${(customInput / 1000).toFixed(0)}K / ${(customOutput / 1000).toFixed(0)}K`
          return (
            <button
              key={key}
              className={`scenario-btn${scenario === key ? ' active' : ''}`}
              onClick={() => selectScenario(key)}
            >
              <span className="dot" style={{ background: s.color }} />
              {label}
              <span className="rate">{rateText}</span>
            </button>
          )
        })}
      </div>

      {scenario === 'custom' && (
        <div className="custom-panel show">
          <div className="custom-grid">
            <div className="input-group">
              <label>{T.inputLabel[lang]}</label>
              <div className="input-row">
                <input
                  type="range" min={1000} max={2_000_000} step={1000}
                  value={customInput}
                  onChange={e => updateCustomInput(Number(e.target.value))}
                />
                <input
                  type="number" min={0} max={10_000_000} step={1000}
                  value={customInput}
                  onChange={e => updateCustomInput(Number(e.target.value))}
                />
                <span className="unit">tok/h</span>
              </div>
            </div>
            <div className="input-group">
              <label>{T.outputLabel[lang]}</label>
              <div className="input-row">
                <input
                  type="range" min={1000} max={1_000_000} step={1000}
                  value={customOutput}
                  onChange={e => updateCustomOutput(Number(e.target.value))}
                />
                <input
                  type="number" min={0} max={5_000_000} step={1000}
                  value={customOutput}
                  onChange={e => updateCustomOutput(Number(e.target.value))}
                />
                <span className="unit">tok/h</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="assumption-bar">
        <span className="lbl">{T.ab_scenario[lang]}</span>
        <span className="val">{T[`sc_${scenario}` as keyof typeof T][lang] as string}</span>
        <span className="sep">·</span>
        <span className="lbl">{T.ab_ratio[lang]}</span>
        <span className="val">{ratio}</span>
        <span className="sep">·</span>
        <span className="lbl">{T.ab_formula[lang]}</span>
        <span className="val" style={{ fontSize: '10px' }}>{costPerH}</span>
      </div>
    </div>
  )
}
