// state/sessionStore.ts
export interface WebSession {
  knowledgeIndex: any
  allowedMetrics: string[]
  blockedMetrics: string[]
  datasetPreview: any[]
  lowTrust: boolean
}

export const session: WebSession = {
  knowledgeIndex: null,
  allowedMetrics: [],
  blockedMetrics: [],
  datasetPreview: [],
  lowTrust: false,
}
