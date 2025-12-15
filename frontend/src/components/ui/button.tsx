import Button from "@mui/material/Button"
import IconButton from "@mui/material/IconButton"
import { styled } from "@mui/material/styles"
import type { ButtonProps } from "@mui/material/Button"
import type { IconButtonProps } from "@mui/material/IconButton"

const StyledButton = styled(Button)(() => ({
  textTransform: "none",
  fontWeight: 500
}))

const StyledIconButton = styled(IconButton)(() => ({
  // Icon button styles
}))

interface CustomButtonProps extends Omit<ButtonProps, "size"> {
  size?: ButtonProps["size"] | "icon"
}

function CustomButton({ size, ...props }: CustomButtonProps) {
  if (size === "icon") {
    return <StyledIconButton size="small" {...(props as IconButtonProps)} />
  }
  return <StyledButton size={size as ButtonProps["size"]} {...props} />
}

export { CustomButton as Button }
