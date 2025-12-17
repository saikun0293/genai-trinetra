import { useState } from "react"
import { ChevronDown, ChevronRight, Brain } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

export interface ThinkingItem {
  agent: string
  message: string
  analysis?: string
  timestamp: number
}

interface ThinkingMessagesProps {
  items: ThinkingItem[]
}

export function ThinkingMessages({ items }: ThinkingMessagesProps) {
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set())

  if (items.length === 0) {
    return null
  }

  const toggleAgent = (agent: string) => {
    const newExpanded = new Set(expandedAgents)
    if (newExpanded.has(agent)) {
      newExpanded.delete(agent)
    } else {
      newExpanded.add(agent)
    }
    setExpandedAgents(newExpanded)
  }

  // Group items by agent
  const groupedItems: Record<string, ThinkingItem[]> = {}
  items.forEach((item) => {
    if (!groupedItems[item.agent]) {
      groupedItems[item.agent] = []
    }
    groupedItems[item.agent].push(item)
  })

  return (
    <div
      className="rounded-lg border mt-2 mb-2"
      style={{
        backgroundColor: "#F9FAFB",
        borderColor: "#E5E7EB"
      }}
    >
      <div className="px-3 py-2">
        <div className="flex items-center gap-2 mb-2">
          <Brain className="w-4 h-4" style={{ color: "#6B7280" }} />
          <span className="text-xs font-medium" style={{ color: "#6B7280" }}>
            Agent Analysis Process
          </span>
        </div>

        <div className="space-y-1">
          {Object.entries(groupedItems).map(([agent, agentItems]) => {
            const isExpanded = expandedAgents.has(agent)
            const latestItem = agentItems[agentItems.length - 1]

            return (
              <div key={agent}>
                <button
                  onClick={() => toggleAgent(agent)}
                  className="w-full flex items-center justify-between px-2 py-1.5 rounded hover:bg-gray-100 transition-colors"
                  style={{
                    backgroundColor: isExpanded ? "#F3F4F6" : "transparent"
                  }}
                >
                  <div className="flex items-center gap-2">
                    {isExpanded ? (
                      <ChevronDown
                        className="w-3 h-3"
                        style={{ color: "#6B7280" }}
                      />
                    ) : (
                      <ChevronRight
                        className="w-3 h-3"
                        style={{ color: "#6B7280" }}
                      />
                    )}
                    <span
                      className="text-xs font-medium"
                      style={{ color: "#374151" }}
                    >
                      {agent}
                    </span>
                  </div>
                  <span className="text-xs" style={{ color: "#9CA3AF" }}>
                    {latestItem.analysis ? "Analysis complete" : "Thinking..."}
                  </span>
                </button>

                {isExpanded && (
                  <div className="ml-7 mt-1 space-y-2 pb-2">
                    {agentItems.map((item, idx) => (
                      <div key={idx} className="space-y-1">
                        {item.message && (
                          <div className="text-xs" style={{ color: "#6B7280" }}>
                            💭 {item.message}
                          </div>
                        )}
                        {item.analysis && (
                          <div
                            className="text-xs p-2 rounded border"
                            style={{
                              backgroundColor: "#FFFFFF",
                              borderColor: "#E5E7EB",
                              color: "#374151"
                            }}
                          >
                            <div className="markdown-thinking prose prose-sm max-w-none">
                              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {item.analysis}
                              </ReactMarkdown>
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
