import Box from "@mui/material/Box"
import { styled } from "@mui/material/styles"

const ScrollArea = styled(Box)(({ theme }) => ({
  overflowY: "auto",
  height: "100%",
  "&::-webkit-scrollbar": {
    width: "8px"
  },
  "&::-webkit-scrollbar-track": {
    background: theme.palette.background.default
  },
  "&::-webkit-scrollbar-thumb": {
    background: theme.palette.action.hover,
    borderRadius: "4px"
  }
}))

const ScrollBar = () => null // MUI handles scrollbars natively

export { ScrollArea, ScrollBar }
