/** pricing.json のスキーマ型定義（Python 側 models.py と同期） */

export type ScrapeStatus = 'success' | 'fallback' | 'manual'

export interface ApiModel {
  provider: string
  name: string
  tag: string
  cls: string
  price_in: number   // USD per 1M input tokens
  price_out: number  // USD per 1M output tokens
  sub_ja: string
  sub_en: string
  scrape_status: ScrapeStatus
}

export interface SubTool {
  group: string
  name: string
  monthly: number
  annual: number | null
  tag: string
  cls: string
  note_ja: string
  note_en: string
  scrape_status: ScrapeStatus
}

export interface PricingData {
  generated_at: string   // ISO 8601
  jpy_rate: number
  jpy_rate_date: string  // YYYY-MM-DD or 'fallback'
  api_models: ApiModel[]
  sub_tools: SubTool[]
}
