import type React from "react"
import Box from "@mui/material/Box"
import Button from "@mui/material/Button"
import IconButton from "@mui/material/IconButton"
import Typography from "@mui/material/Typography"
import Chip from "@mui/material/Chip"
import Link from "@mui/material/Link"
import CircularProgress from "@mui/material/CircularProgress"
import { Copy, CopyCheck } from "lucide-react"
import { InputForm } from "@/components/InputForm"
import { useState, ReactNode } from "react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { cn } from "@/utils"
import { ActivityTimeline } from "@/components/ActivityTimeline"

// Markdown component props type from former ReportView
type MdComponentProps = {
  className?: string
  children?: ReactNode
  [key: string]: any
}

interface ProcessedEvent {
  title: string
  data: any
}

// Markdown components (from former ReportView.tsx)
const mdComponents = {
  h1: ({ className, children, ...props }: MdComponentProps) => (
    <h1 className={cn("text-2xl font-bold mt-4 mb-2", className)} {...props}>
      {children}
    </h1>
  ),
  h2: ({ className, children, ...props }: MdComponentProps) => (
    <h2 className={cn("text-xl font-bold mt-3 mb-2", className)} {...props}>
      {children}
    </h2>
  ),
  h3: ({ className, children, ...props }: MdComponentProps) => (
    <h3 className={cn("text-lg font-bold mt-3 mb-1", className)} {...props}>
      {children}
    </h3>
  ),
  p: ({ className, children, ...props }: MdComponentProps) => (
    <p className={cn("mb-3 leading-7", className)} {...props}>
      {children}
    </p>
  ),
  a: ({ className, children, href, ...props }: MdComponentProps) => (
    <Chip
      size="small"
      label={
        <Link
          className={cn("text-xs", className)}
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          underline="hover"
          sx={{ color: "inherit" }}
          {...props}
        >
          {children}
        </Link>
      }
      sx={{
        backgroundColor: "primary.main",
        color: "primary.contrastText",
        height: "auto",
        "& .MuiChip-label": { padding: "2px 8px" }
      }}
    />
  ),
  ul: ({ className, children, ...props }: MdComponentProps) => (
    <ul className={cn("list-disc pl-6 mb-3", className)} {...props}>
      {children}
    </ul>
  ),
  ol: ({ className, children, ...props }: MdComponentProps) => (
    <ol className={cn("list-decimal pl-6 mb-3", className)} {...props}>
      {children}
    </ol>
  ),
  li: ({ className, children, ...props }: MdComponentProps) => (
    <li className={cn("mb-1", className)} {...props}>
      {children}
    </li>
  ),
  blockquote: ({ className, children, ...props }: MdComponentProps) => (
    <blockquote
      className={cn(
        "border-l-4 border-neutral-600 pl-4 italic my-3 text-sm",
        className
      )}
      {...props}
    >
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }: MdComponentProps) => (
    <code
      className={cn(
        "bg-neutral-900 rounded px-1 py-0.5 font-mono text-xs",
        className
      )}
      {...props}
    >
      {children}
    </code>
  ),
  pre: ({ className, children, ...props }: MdComponentProps) => (
    <pre
      className={cn(
        "bg-neutral-900 p-3 rounded-lg overflow-x-auto font-mono text-xs my-3",
        className
      )}
      {...props}
    >
      {children}
    </pre>
  ),
  hr: ({ className, ...props }: MdComponentProps) => (
    <hr className={cn("border-neutral-600 my-4", className)} {...props} />
  ),
  table: ({ className, children, ...props }: MdComponentProps) => (
    <div className="my-3 overflow-x-auto">
      <table className={cn("border-collapse w-full", className)} {...props}>
        {children}
      </table>
    </div>
  ),
  th: ({ className, children, ...props }: MdComponentProps) => (
    <th
      className={cn(
        "border border-neutral-600 px-3 py-2 text-left font-bold",
        className
      )}
      {...props}
    >
      {children}
    </th>
  ),
  td: ({ className, children, ...props }: MdComponentProps) => (
    <td
      className={cn("border border-neutral-600 px-3 py-2", className)}
      {...props}
    >
      {children}
    </td>
  )
}

// Props for HumanMessageBubble
interface HumanMessageBubbleProps {
  message: { content: string; id: string }
  mdComponents: typeof mdComponents
}

// HumanMessageBubble Component
const HumanMessageBubble: React.FC<HumanMessageBubbleProps> = ({
  message,
  mdComponents
}) => {
  return (
    <Box
      sx={{
        color: "white",
        borderRadius: 3,
        wordBreak: "break-word",
        minHeight: 28,
        backgroundColor: "rgba(82, 82, 82, 0.9)",
        maxWidth: { xs: "100%", sm: "90%" },
        px: 3,
        pt: 2,
        pb: 1,
        borderBottomRightRadius: 1
      }}
    >
      <ReactMarkdown components={mdComponents} remarkPlugins={[remarkGfm]}>
        {message.content}
      </ReactMarkdown>
    </Box>
  )
}

// Props for AiMessageBubble
interface AiMessageBubbleProps {
  message: { content: string; id: string }
  mdComponents: typeof mdComponents
  handleCopy: (text: string, messageId: string) => void
  copiedMessageId: string | null
  agent?: string
  finalReportWithCitations?: boolean
  processedEvents: ProcessedEvent[]
  websiteCount: number
  isLoading: boolean
}

// AiMessageBubble Component
const AiMessageBubble: React.FC<AiMessageBubbleProps> = ({
  message,
  mdComponents,
  handleCopy,
  copiedMessageId,
  agent,
  finalReportWithCitations,
  processedEvents,
  websiteCount,
  isLoading
}) => {
  // Show ActivityTimeline if we have processedEvents (this will be the first AI message)
  const shouldShowTimeline = processedEvents.length > 0

  // Condition for DIRECT DISPLAY (interactive_planner_agent OR final report)
  const shouldDisplayDirectly =
    agent === "interactive_planner_agent" ||
    (agent === "report_composer_with_citations" && finalReportWithCitations)

  if (shouldDisplayDirectly) {
    return (
      <Box
        sx={{
          position: "relative",
          wordBreak: "break-word",
          display: "flex",
          flexDirection: "column",
          width: "100%"
        }}
      >
        {shouldShowTimeline && agent === "interactive_planner_agent" && (
          <Box sx={{ width: "100%", mb: 2 }}>
            <ActivityTimeline
              processedEvents={processedEvents}
              isLoading={isLoading}
              websiteCount={websiteCount}
            />
          </Box>
        )}
        <Box sx={{ display: "flex", alignItems: "flex-start", gap: 2 }}>
          <Box sx={{ flex: 1 }}>
            <ReactMarkdown
              components={mdComponents}
              remarkPlugins={[remarkGfm]}
            >
              {message.content}
            </ReactMarkdown>
          </Box>
          <IconButton
            size="small"
            onClick={() => handleCopy(message.content, message.id)}
            sx={{
              color:
                copiedMessageId === message.id
                  ? "success.main"
                  : "text.secondary",
              "&:hover": { backgroundColor: "action.hover" }
            }}
          >
            {copiedMessageId === message.id ? (
              <CopyCheck size={16} />
            ) : (
              <Copy size={16} />
            )}
          </IconButton>
        </Box>
      </Box>
    )
  } else if (shouldShowTimeline) {
    return (
      <Box
        sx={{
          position: "relative",
          wordBreak: "break-word",
          display: "flex",
          flexDirection: "column",
          width: "100%"
        }}
      >
        <Box sx={{ width: "100%" }}>
          <ActivityTimeline
            processedEvents={processedEvents}
            isLoading={isLoading}
            websiteCount={websiteCount}
          />
        </Box>
        {message.content &&
          message.content.trim() &&
          agent !== "interactive_planner_agent" && (
            <Box
              sx={{ display: "flex", alignItems: "flex-start", gap: 2, mt: 2 }}
            >
              <Box sx={{ flex: 1 }}>
                <ReactMarkdown
                  components={mdComponents}
                  remarkPlugins={[remarkGfm]}
                >
                  {message.content}
                </ReactMarkdown>
              </Box>
              <IconButton
                size="small"
                onClick={() => handleCopy(message.content, message.id)}
                sx={{
                  color:
                    copiedMessageId === message.id
                      ? "success.main"
                      : "text.secondary",
                  "&:hover": { backgroundColor: "action.hover" }
                }}
              >
                {copiedMessageId === message.id ? (
                  <CopyCheck size={16} />
                ) : (
                  <Copy size={16} />
                )}
              </IconButton>
            </Box>
          )}
      </Box>
    )
  } else {
    return (
      <Box
        sx={{
          position: "relative",
          wordBreak: "break-word",
          display: "flex",
          flexDirection: "column",
          width: "100%"
        }}
      >
        <Box sx={{ display: "flex", alignItems: "flex-start", gap: 2 }}>
          <Box sx={{ flex: 1 }}>
            <ReactMarkdown
              components={mdComponents}
              remarkPlugins={[remarkGfm]}
            >
              {message.content}
            </ReactMarkdown>
          </Box>
          <IconButton
            size="small"
            onClick={() => handleCopy(message.content, message.id)}
            sx={{
              color:
                copiedMessageId === message.id
                  ? "success.main"
                  : "text.secondary",
              "&:hover": { backgroundColor: "action.hover" }
            }}
          >
            {copiedMessageId === message.id ? (
              <CopyCheck size={16} />
            ) : (
              <Copy size={16} />
            )}
          </IconButton>
        </Box>
      </Box>
    )
  }
}

interface ChatMessagesViewProps {
  messages: {
    type: "human" | "ai"
    content: string
    id: string
    agent?: string
    finalReportWithCitations?: boolean
  }[]
  isLoading: boolean
  scrollAreaRef: React.RefObject<HTMLDivElement | null>
  onSubmit: (query: string) => void
  onCancel: () => void
  displayData: string | null
  messageEvents: Map<string, ProcessedEvent[]>
  websiteCount: number
}

export function ChatMessagesView({
  messages,
  isLoading,
  scrollAreaRef,
  onSubmit,
  onCancel,
  messageEvents,
  websiteCount
}: ChatMessagesViewProps) {
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null)

  const handleCopy = async (text: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedMessageId(messageId)
      setTimeout(() => setCopiedMessageId(null), 2000)
    } catch (err) {
      console.error("Failed to copy text:", err)
    }
  }

  const handleNewChat = () => {
    window.location.reload()
  }

  // Find the ID of the last AI message
  const lastAiMessage = messages
    .slice()
    .reverse()
    .find((m) => m.type === "ai")
  const lastAiMessageId = lastAiMessage?.id

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        height: "100%",
        width: "100%"
      }}
    >
      {/* Header with New Chat button */}
      <Box
        sx={{
          borderBottom: 1,
          borderColor: "divider",
          p: 2,
          backgroundColor: "background.paper"
        }}
      >
        <Box
          sx={{
            maxWidth: 1200,
            mx: "auto",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}
        >
          <Typography variant="h6" component="h1" sx={{ fontWeight: 600 }}>
            Chat
          </Typography>
          <Button
            onClick={handleNewChat}
            variant="outlined"
            sx={{ textTransform: "none" }}
          >
            New Chat
          </Button>
        </Box>
      </Box>
      <Box
        sx={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          width: "100%",
          overflow: "hidden"
        }}
      >
        <Box
          ref={scrollAreaRef}
          sx={{
            flex: 1,
            width: "100%",
            overflowY: "auto",
            overflowX: "hidden"
          }}
        >
          <Box
            sx={{
              p: { xs: 2, md: 3 },
              maxWidth: 1200,
              mx: "auto",
              display: "flex",
              flexDirection: "column",
              gap: 2
            }}
          >
            {messages.map((message) => {
              const eventsForMessage =
                message.type === "ai" ? messageEvents.get(message.id) || [] : []

              const isCurrentMessageTheLastAiMessage =
                message.type === "ai" && message.id === lastAiMessageId

              return (
                <Box
                  key={message.id}
                  sx={{
                    display: "flex",
                    justifyContent:
                      message.type === "human" ? "flex-end" : "flex-start"
                  }}
                >
                  {message.type === "human" ? (
                    <HumanMessageBubble
                      message={message}
                      mdComponents={mdComponents}
                    />
                  ) : (
                    <AiMessageBubble
                      message={message}
                      mdComponents={mdComponents}
                      handleCopy={handleCopy}
                      copiedMessageId={copiedMessageId}
                      agent={message.agent}
                      finalReportWithCitations={
                        message.finalReportWithCitations
                      }
                      processedEvents={eventsForMessage}
                      websiteCount={
                        isCurrentMessageTheLastAiMessage ? websiteCount : 0
                      }
                      isLoading={isCurrentMessageTheLastAiMessage && isLoading}
                    />
                  )}
                </Box>
              )
            })}
            {isLoading &&
              !lastAiMessage &&
              messages.some((m) => m.type === "human") && (
                <Box sx={{ display: "flex", justifyContent: "flex-start" }}>
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      color: "text.secondary"
                    }}
                  >
                    <CircularProgress size={16} />
                    <Typography variant="body2">Thinking...</Typography>
                  </Box>
                </Box>
              )}
            {isLoading &&
              messages.length > 0 &&
              messages[messages.length - 1].type === "human" && (
                <Box
                  sx={{
                    display: "flex",
                    justifyContent: "flex-start",
                    pl: 2,
                    pt: 1
                  }}
                >
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      color: "text.secondary"
                    }}
                  >
                    <CircularProgress size={16} />
                    <Typography variant="body2">Thinking...</Typography>
                  </Box>
                </Box>
              )}
          </Box>
        </Box>
      </Box>
      <Box
        sx={{
          borderTop: 1,
          borderColor: "divider",
          p: 2,
          width: "100%",
          backgroundColor: "background.paper"
        }}
      >
        <Box sx={{ maxWidth: 900, mx: "auto" }}>
          <InputForm onSubmit={onSubmit} isLoading={isLoading} context="chat" />
          {isLoading && (
            <Box sx={{ mt: 2, display: "flex", justifyContent: "center" }}>
              <Button
                variant="outlined"
                color="error"
                onClick={onCancel}
                sx={{ textTransform: "none" }}
              >
                Cancel
              </Button>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  )
}
