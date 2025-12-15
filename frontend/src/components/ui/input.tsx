import TextField from "@mui/material/TextField"
import { styled } from "@mui/material/styles"

const StyledInput = styled(TextField)(({ theme }) => ({
  "& .MuiOutlinedInput-root": {
    borderRadius: theme.shape.borderRadius
  }
}))

export { StyledInput as Input }
