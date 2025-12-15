import TextField from "@mui/material/TextField"
import { styled } from "@mui/material/styles"

const Textarea = styled(TextField)(({ theme }) => ({
  width: "100%",
  "& .MuiOutlinedInput-root": {
    borderRadius: theme.shape.borderRadius
  }
}))

export { Textarea }
