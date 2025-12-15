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
    onChunk?: (text: string) => void
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

                // Extract text from the response
                if (data.content?.parts) {
                  for (const part of data.content.parts) {
                    if (part.text) {
                      fullText += part.text
                      if (onChunk) {
                        onChunk(part.text)
                      }
                    }
                  }
                }
              } catch (e) {
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

    return fullText
  }

  resetSession() {
    this.currentSessionId = null
  }

  getCurrentSessionId(): string | null {
    return this.currentSessionId
  }
}

export const agentService = new AgentService()
