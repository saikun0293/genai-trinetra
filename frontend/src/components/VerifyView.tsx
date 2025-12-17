import { useState, useRef, useEffect } from "react"
import { Send, Loader2, Trash2, User, Bot } from "lucide-react"
import { agentService, ThinkingMessage } from "@/services/agentService"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { ThinkingMessages, ThinkingItem } from "./ThinkingMessages"

export interface ChatMessage {
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

interface VerifyViewProps {
  messages: ChatMessage[]
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>
  onAnalysisComplete?: () => void
}

export function VerifyView({
  messages,
  setMessages,
  onAnalysisComplete
}: VerifyViewProps) {
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [streamingText, setStreamingText] = useState("")
  const [statusMessageIndex, setStatusMessageIndex] = useState(0)
  const [agentProgress, setAgentProgress] = useState<string[]>([])
  const [currentAnalysisItems, setCurrentAnalysisItems] = useState<
    ThinkingItem[]
  >([])
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const statusMessages = [
    "Analyzing transaction...",
    "Checking compliance rules...",
    "Verifying payment details...",
    "Consulting risk database...",
    "Evaluating geopolitical factors...",
    "Cross-referencing vendor data...",
    "Finalizing assessment..."
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingText])

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null

    if (isLoading && !streamingText) {
      // Reset to first message when loading starts
      setStatusMessageIndex(0)

      // Rotate through status messages every 5 seconds
      interval = setInterval(() => {
        setStatusMessageIndex((prev) => (prev + 1) % statusMessages.length)
      }, 10000)
    }

    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [isLoading, streamingText, statusMessages.length])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: ChatMessage = {
      role: "user",
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)
    setStreamingText("")
    setAgentProgress([])
    setCurrentAnalysisItems([])

    try {
      const response = await agentService.sendMessage(
        userMessage.content,
        "app",
        undefined, // Don't stream chunks to chat - only show final report
        undefined, // Don't track thinking messages
        (analysisMessage) => {
          // Track analysis messages in the accordion
          console.log("Adding analysis from:", analysisMessage.agent)
          setCurrentAnalysisItems((prev) => [
            ...prev,
            {
              agent: analysisMessage.agent,
              message: "",
              analysis: analysisMessage.analysis,
              timestamp: analysisMessage.timestamp
            }
          ])
        }
      )

      console.log("Analysis complete, response length:", response?.length || 0)

      // Extract the critique_agent_response_markdown if present
      let displayContent =
        response ||
        "Analysis complete. View the transaction details to see the full analysis."

      if (response?.includes("critique_agent_response_markdown")) {
        try {
          // Extract the markdown report from the JSON response
          const markdownMatch = response.match(
            /"critique_agent_response_markdown":\s*"([^"]*(?:\\.[^"]*)*)"/
          )
          if (markdownMatch) {
            // Unescape the JSON string
            displayContent = markdownMatch[1]
              .replace(/\\n/g, "\n")
              .replace(/\\"/g, '"')
              .replace(/\\\\/g, "\\")
            console.log(
              "Extracted critique markdown, length:",
              displayContent.length
            )
          }
        } catch (e) {
          console.error("Failed to extract critique markdown:", e)
        }
      }

      // Only include meaningful response
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: displayContent,
        timestamp: new Date()
      }

      setMessages((prev) => [...prev, assistantMessage])
      setStreamingText("")
      setAgentProgress([])
      setCurrentAnalysisItems([])

      // Refresh transactions if analysis was completed successfully
      if (onAnalysisComplete && response && !response.includes("error")) {
        setTimeout(() => {
          onAnalysisComplete()
        }, 1000) // Small delay to ensure backend has updated
      }
    } catch (error) {
      console.error("Error sending message:", error)

      // Check if it's a context variable error
      let errorContent = "Sorry, I encountered an error. Please try again."
      if (error instanceof Error) {
        if (error.message.includes("Context variable not found")) {
          errorContent = `⚠️ **Analysis Error**: One or more agents failed to complete their analysis.\n\nThis usually means the agents couldn't access required data. Please try again or contact support if the issue persists.\n\nError details: ${error.message}`
        } else {
          errorContent = `⚠️ **Error**: ${error.message}\n\nPlease try again.`
        }
      }

      const errorMessage: ChatMessage = {
        role: "assistant",
        content: errorContent,
        timestamp: new Date()
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleClearChat = () => {
    setMessages([])
    agentService.resetSession()
    setStreamingText("")
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div
      className="flex flex-col h-full"
      style={{ backgroundColor: "#F0F4F8" }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-6 py-4 border-b"
        style={{
          backgroundColor: "#FFFFFF",
          borderColor: "#D0D5DD"
        }}
      >
        <div>
          <h2 className="text-2xl font-bold" style={{ color: "#000000" }}>
            Transaction Verification Agent
          </h2>
          <p className="text-sm mt-1" style={{ color: "#3B4953" }}>
            Chat with the AI agent to verify and analyze transactions
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearChat}
            className="flex items-center gap-2 px-4 py-2 rounded transition-all hover:opacity-80"
            style={{ backgroundColor: "#E9EEF6", color: "#3B4953" }}
            title="Clear conversation"
          >
            <Trash2 className="w-4 h-4" />
            Clear Chat
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 && !streamingText && (
          <div className="flex flex-col items-center justify-center h-full">
            <div
              className="w-20 h-20 rounded-full flex items-center justify-center mb-4"
              style={{ backgroundColor: "#E9EEF6" }}
            >
              <Bot className="w-10 h-10" style={{ color: "#3b82f6" }} />
            </div>
            <h3
              className="text-xl font-semibold mb-2"
              style={{ color: "#000000" }}
            >
              Welcome to Transaction Verification
            </h3>
            <p className="text-center max-w-md" style={{ color: "#3B4953" }}>
              Ask me to analyze transactions, check compliance, or verify
              payment details. I can help you understand risk factors and make
              informed decisions.
            </p>
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
              {[
                "Analyze transaction 17a3fbcb-7b3f-4984-a384-0f9be1057895",
                "I think this transaction looks suspicious, can you verify?"
              ].map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setInput(suggestion)}
                  className="px-4 py-3 rounded text-left text-sm transition-all hover:opacity-80"
                  style={{
                    backgroundColor: "#FFFFFF",
                    color: "#3B4953",
                    border: "1px solid #D0D5DD"
                  }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex gap-3 ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {message.role === "assistant" && (
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                  style={{ backgroundColor: "#E9EEF6" }}
                >
                  <Bot className="w-5 h-5" style={{ color: "#3b82f6" }} />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === "user" ? "order-1" : ""
                }`}
                style={{
                  backgroundColor:
                    message.role === "user" ? "#2563EB" : "#FFFFFF",
                  color: message.role === "user" ? "#FFFFFF" : "#000000",
                  wordBreak: "break-word",
                  overflowWrap: "anywhere",
                  border:
                    message.role === "assistant" ? "1px solid #D0D5DD" : "none"
                }}
              >
                {message.role === "assistant" ? (
                  <>
                    <div className="markdown-analysis max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  </>
                ) : (
                  <p className="whitespace-pre-wrap break-words overflow-wrap-anywhere">
                    {message.content}
                  </p>
                )}
                <p
                  className="text-xs mt-2 opacity-70"
                  style={{
                    color: message.role === "user" ? "#E0E7FF" : "#3B4953"
                  }}
                >
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
              {message.role === "user" && (
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 order-2"
                  style={{ backgroundColor: "#E9EEF6" }}
                >
                  <User className="w-5 h-5" style={{ color: "#3b82f6" }} />
                </div>
              )}
            </div>
          ))}

          {/* Streaming/Loading message - show only one state */}
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: "#E9EEF6" }}
              >
                <Bot className="w-5 h-5" style={{ color: "#3b82f6" }} />
              </div>
              <div
                className="max-w-[80%] rounded-lg px-4 py-3"
                style={{
                  backgroundColor: "#FFFFFF",
                  color: "#000000",
                  border: "1px solid #D0D5DD"
                }}
              >
                {currentAnalysisItems.length > 0 && (
                  <div className="mb-3">
                    <ThinkingMessages items={currentAnalysisItems} />
                  </div>
                )}
                <div className="flex items-center gap-2 mb-2">
                  <Loader2
                    className="w-4 h-4 animate-spin"
                    style={{ color: "#3b82f6" }}
                  />
                  <p
                    className="text-sm font-medium"
                    style={{ color: "#3B4953" }}
                  >
                    {statusMessages[statusMessageIndex]}
                  </p>
                </div>
                <p className="text-xs" style={{ color: "#6B7280" }}>
                  Running compliance analysis agents...
                </p>
              </div>
              </div>
            </div>
          )}
        </div>

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div
        className="border-t px-6 py-4"
        style={{
          backgroundColor: "#FFFFFF",
          borderColor: "#D0D5DD"
        }}
      >
        <form onSubmit={handleSubmit} className="flex gap-3">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about transactions, compliance, or risk analysis..."
            rows={2}
            className="flex-1 rounded-lg px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{
              backgroundColor: "#F0F4F8",
              color: "#000000",
              border: "1px solid #D0D5DD"
            }}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-6 rounded-lg transition-all hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            style={{
              backgroundColor: "#2563EB",
              color: "#FFFFFF"
            }}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Sending...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Send
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
