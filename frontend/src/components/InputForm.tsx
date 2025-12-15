import { useState, useRef, useEffect } from "react"
import Box from "@mui/material/Box"
import TextField from "@mui/material/TextField"
import IconButton from "@mui/material/IconButton"
import CircularProgress from "@mui/material/CircularProgress"
import { Send } from "lucide-react"

interface InputFormProps {
  onSubmit: (query: string) => void
  isLoading: boolean
  context?: "homepage" | "chat"
}

export function InputForm({
  onSubmit,
  isLoading,
  context = "homepage"
}: InputFormProps) {
  const [inputValue, setInputValue] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus()
    }
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim() && !isLoading) {
      onSubmit(inputValue.trim())
      setInputValue("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const placeholderText =
    context === "chat"
      ? "Respond to the Agent, refine the plan, or type 'Looks good'..."
      : "Ask me anything... e.g., A report on the latest Google I/O"

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: "flex", gap: 1, alignItems: "flex-end" }}
    >
      <TextField
        inputRef={textareaRef}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholderText}
        multiline
        minRows={1}
        maxRows={6}
        fullWidth
        variant="outlined"
        sx={{
          "& .MuiOutlinedInput-root": {
            backgroundColor: "background.paper"
          }
        }}
      />
      <IconButton
        type="submit"
        color="primary"
        disabled={isLoading || !inputValue.trim()}
        sx={{
          width: 48,
          height: 48,
          backgroundColor: "primary.main",
          color: "primary.contrastText",
          "&:hover": {
            backgroundColor: "primary.dark"
          },
          "&:disabled": {
            backgroundColor: "action.disabledBackground"
          }
        }}
      >
        {isLoading ? (
          <CircularProgress size={20} color="inherit" />
        ) : (
          <Send size={20} />
        )}
      </IconButton>
    </Box>
  )
}
