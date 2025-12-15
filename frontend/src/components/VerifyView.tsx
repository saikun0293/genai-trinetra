import { useState, useRef, useEffect } from "react"
import { Send, Loader2, Trash2, User, Bot } from "lucide-react"
import { agentService } from "@/services/agentService"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface ChatMessage {
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export function VerifyView() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [streamingText, setStreamingText] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingText])

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

    try {
      const response = await agentService.sendMessage(
        userMessage.content,
        "app",
        (chunk) => {
          setStreamingText((prev) => prev + chunk)
        }
      )

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response,
        timestamp: new Date()
      }

      setMessages((prev) => [...prev, assistantMessage])
      setStreamingText("")
    } catch (error) {
      console.error("Error sending message:", error)
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
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
      style={{ backgroundColor: "#0F1011" }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between px-6 py-4 border-b"
        style={{
          backgroundColor: "#17181A",
          borderColor: "#2D2E2F"
        }}
      >
        <div>
          <h2 className="text-2xl font-bold" style={{ color: "#E8EAED" }}>
            Transaction Verification Agent
          </h2>
          <p className="text-sm mt-1" style={{ color: "#B8BCC1" }}>
            Chat with the AI agent to verify and analyze transactions
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearChat}
            className="flex items-center gap-2 px-4 py-2 rounded transition-all hover:opacity-80"
            style={{ backgroundColor: "#2D2E2F", color: "#B8BCC1" }}
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
              style={{ backgroundColor: "#2D2E2F" }}
            >
              <Bot className="w-10 h-10" style={{ color: "#60A5FA" }} />
            </div>
            <h3
              className="text-xl font-semibold mb-2"
              style={{ color: "#E8EAED" }}
            >
              Welcome to Transaction Verification
            </h3>
            <p className="text-center max-w-md" style={{ color: "#B8BCC1" }}>
              Ask me to analyze transactions, check compliance, or verify
              payment details. I can help you understand risk factors and make
              informed decisions.
            </p>
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
              {[
                "Analyze transaction TXN_001",
                "Check compliance for payment to Canada",
                "What are the risk factors?",
                "Verify vendor information"
              ].map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setInput(suggestion)}
                  className="px-4 py-3 rounded text-left text-sm transition-all hover:opacity-80"
                  style={{
                    backgroundColor: "#1E1F20",
                    color: "#B8BCC1",
                    border: "1px solid #2D2E2F"
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
                  style={{ backgroundColor: "#2D2E2F" }}
                >
                  <Bot className="w-5 h-5" style={{ color: "#60A5FA" }} />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === "user" ? "order-1" : ""
                }`}
                style={{
                  backgroundColor:
                    message.role === "user" ? "#2563EB" : "#1E1F20",
                  color: message.role === "user" ? "#FFFFFF" : "#E8EAED"
                }}
              >
                {message.role === "assistant" ? (
                  <div className="prose prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p className="whitespace-pre-wrap">{message.content}</p>
                )}
                <p
                  className="text-xs mt-2 opacity-70"
                  style={{
                    color: message.role === "user" ? "#E0E7FF" : "#B8BCC1"
                  }}
                >
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
              {message.role === "user" && (
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 order-2"
                  style={{ backgroundColor: "#2D2E2F" }}
                >
                  <User className="w-5 h-5" style={{ color: "#60A5FA" }} />
                </div>
              )}
            </div>
          ))}

          {/* Streaming message */}
          {streamingText && (
            <div className="flex gap-3 justify-start">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                style={{ backgroundColor: "#2D2E2F" }}
              >
                <Bot className="w-5 h-5" style={{ color: "#60A5FA" }} />
              </div>
              <div
                className="max-w-[80%] rounded-lg px-4 py-3"
                style={{ backgroundColor: "#1E1F20", color: "#E8EAED" }}
              >
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {streamingText}
                  </ReactMarkdown>
                </div>
                <div className="flex items-center gap-1 mt-2">
                  <Loader2
                    className="w-3 h-3 animate-spin"
                    style={{ color: "#60A5FA" }}
                  />
                  <p className="text-xs" style={{ color: "#B8BCC1" }}>
                    Thinking...
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
          backgroundColor: "#17181A",
          borderColor: "#2D2E2F"
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
              backgroundColor: "#2D2E2F",
              color: "#E8EAED",
              border: "1px solid #3C3D3F"
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
