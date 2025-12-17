interface CreateSessionResponse {
  id: string
  user_id: string
  app_name: string
  state: Record<string, unknown>
}

interface AgentResponse {
  content?: {
    role: string
    parts: Array<{ text?: string }>
  }
  type?: string
}

interface ThinkingMessage {
  agent: string
  message: string
  timestamp: number
}

interface AnalysisMessage {
  agent: string
  analysis: string
  timestamp: number
}

interface AnalysisData {
  transaction_id: string
  payee_analysis: string | null
  payer_analysis: string | null
  geopolitical_analysis: string | null
  transaction_analysis: string | null
  critic_analysis: string | null
}

interface AnalysisResponse {
  success: boolean
  transaction_id: string
  analysis: AnalysisData
}

class AgentService {
  private baseUrl = "" // Empty string uses current origin with Vite proxy
  private currentSessionId: string | null = null
  private currentUserId: string = "user_" + Date.now()

  async createSession(appName: string = "app"): Promise<string> {
    const response = await fetch(
      `${this.baseUrl}/apps/${appName}/users/${this.currentUserId}/sessions`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({})
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.statusText}`)
    }

    const data: CreateSessionResponse = await response.json()
    this.currentSessionId = data.id
    return data.id
  }

  async sendMessage(
    message: string,
    appName: string = "app",
    onChunk?: (text: string) => void,
    onThinking?: (thinking: ThinkingMessage) => void,
    onAnalysis?: (analysis: AnalysisMessage) => void
  ): Promise<string> {
    // Create session if not exists
    if (!this.currentSessionId) {
      await this.createSession(appName)
    }

    const response = await fetch(`${this.baseUrl}/run_sse`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        app_name: appName,
        user_id: this.currentUserId,
        session_id: this.currentSessionId,
        new_message: {
          role: "user",
          parts: [{ text: message }]
        }
      })
    })

    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.statusText}`)
    }

    // Handle streaming response
    const reader = response.body?.getReader()
    const decoder = new TextDecoder()
    let fullText = ""
    let hasError = false
    let errorDetails = ""

    if (reader) {
      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value, { stream: true })
          const lines = chunk.split("\n")

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const jsonStr = line.slice(6)
                if (jsonStr.trim() === "[DONE]") continue

                const data: AgentResponse = JSON.parse(jsonStr)

                // Check if this is an error response
                if (data.type === "error" || (data as any).error) {
                  hasError = true
                  errorDetails = (data as any).error || JSON.stringify(data)
                  throw new Error(errorDetails)
                }

                // Extract text from the response
                if (data.content?.parts) {
                  for (const part of data.content.parts) {
                    if (part.text) {
                      // Check if this is a thinking message
                      const thinkingMatch = part.text.match(
                        /^\[THINKING:(.*?)\]\s*(.*)$/
                      )
                      if (thinkingMatch && onThinking) {
                        const [, agent, message] = thinkingMatch
                        onThinking({
                          agent: agent.trim(),
                          message: message.trim(),
                          timestamp: Date.now()
                        })
                        continue
                      }

                      // Check if this is an analysis message
                      const analysisMatch = part.text.match(
                        /^\[ANALYSIS:(.*?)\]\n(.*)$/s
                      )
                      if (analysisMatch && onAnalysis) {
                        const [, agent, analysis] = analysisMatch
                        onAnalysis({
                          agent: agent.trim(),
                          analysis: analysis.trim(),
                          timestamp: Date.now()
                        })
                        continue
                      }

                      // Regular message
                      fullText += part.text
                      if (onChunk) {
                        onChunk(part.text)
                      }
                    }
                  }
                }
              } catch (e) {
                // If it's our thrown error, re-throw it
                if (hasError) {
                  throw e
                }
                // Skip invalid JSON
                console.debug("Skipping invalid JSON chunk:", e)
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }
    }

    // Check if we got an error in the response
    if (hasError) {
      throw new Error(errorDetails)
    }

    return fullText
  }

  async getTransactionAnalysis(
    transactionId: string
  ): Promise<AnalysisData | null> {
    try {
      const response = await fetch(
        `${this.baseUrl}/api/analysis/${transactionId}`
      )

      if (response.status === 404) {
        // No analysis found for this transaction
        return null
      }

      if (!response.ok) {
        throw new Error(`Failed to fetch analysis: ${response.statusText}`)
      }

      const data: AnalysisResponse = await response.json()
      return data.analysis
    } catch (error) {
      console.error(`Error fetching analysis for ${transactionId}:`, error)
      return null
    }
  }

  resetSession() {
    this.currentSessionId = null
  }

  getCurrentSessionId(): string | null {
    return this.currentSessionId
  }
}

export const agentService = new AgentService()
export type { ThinkingMessage, AnalysisMessage }
