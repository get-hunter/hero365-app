import React, { useState } from "react"
import { Button } from "./button"
import { Box, HStack, Input, Text, VStack } from "@chakra-ui/react"
import { FiPhone } from "react-icons/fi"
import { Field } from "./field"
import { InputGroup } from "./input-group"

interface PhoneAuthProps {
  onSendOTP: (phone: string) => Promise<void>
  onVerifyOTP: (phone: string, otp: string) => Promise<void>
  loading?: boolean
  error?: string | null
}

export function PhoneAuth({ onSendOTP, onVerifyOTP, loading = false, error }: PhoneAuthProps) {
  const [phone, setPhone] = useState("")
  const [otp, setOtp] = useState("")
  const [step, setStep] = useState<"phone" | "otp">("phone")
  const [otpSent, setOtpSent] = useState(false)

  const handleSendOTP = async () => {
    if (!phone.trim()) return
    
    try {
      await onSendOTP(phone)
      setOtpSent(true)
      setStep("otp")
    } catch (error) {
      console.error("Failed to send OTP:", error)
    }
  }

  const handleVerifyOTP = async () => {
    if (!otp.trim() || otp.length < 6) return
    
    try {
      await onVerifyOTP(phone, otp)
    } catch (error) {
      console.error("Failed to verify OTP:", error)
    }
  }

  const handleBackToPhone = () => {
    setStep("phone")
    setOtp("")
    setOtpSent(false)
  }

  if (step === "otp") {
    return (
      <VStack gap={4} width="100%">
        <Box textAlign="center">
          <Text fontWeight="semibold" mb={2}>
            Verify Phone Number
          </Text>
          <Text fontSize="sm" color="gray.600">
            Enter the 6-digit code sent to {phone}
          </Text>
        </Box>

        <Box>
          <HStack gap={2} justify="center">
            <Input
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="123456"
              textAlign="center"
              maxLength={6}
              size="lg"
              letterSpacing="0.5em"
              fontFamily="mono"
            />
          </HStack>
        </Box>

        {error && (
          <Text color="red.500" fontSize="sm" textAlign="center">
            {error}
          </Text>
        )}

        <VStack gap={2} width="100%">
          <Button
            onClick={handleVerifyOTP}
            loading={loading}
            disabled={otp.length < 6}
            width="100%"
            variant="solid"
          >
            Verify Code
          </Button>
          
          <Button
            onClick={handleBackToPhone}
            variant="ghost"
            size="sm"
            disabled={loading}
          >
            Change Phone Number
          </Button>
        </VStack>
      </VStack>
    )
  }

  return (
    <VStack gap={4} width="100%">
      <Box textAlign="center">
        <Text fontWeight="semibold" mb={2}>
          Sign in with Phone
        </Text>
        <Text fontSize="sm" color="gray.600">
          Enter your phone number to receive a verification code
        </Text>
      </Box>

      <Field invalid={!!error} errorText={error}>
        <InputGroup startElement={<FiPhone />}>
          <Input
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+1 (555) 123-4567"
            type="tel"
            size="lg"
          />
        </InputGroup>
      </Field>

      <Button
        onClick={handleSendOTP}
        loading={loading}
        disabled={!phone.trim()}
        width="100%"
        variant="solid"
      >
        Send Verification Code
      </Button>
    </VStack>
  )
}

interface PhoneSignupProps {
  onSignup: (phone: string, password: string, fullName?: string) => Promise<void>
  loading?: boolean
  error?: string | null
}

export function PhoneSignup({ onSignup, loading = false, error }: PhoneSignupProps) {
  const [phone, setPhone] = useState("")
  const [password, setPassword] = useState("")
  const [fullName, setFullName] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!phone.trim() || !password.trim()) return
    
    try {
      await onSignup(phone, password, fullName || undefined)
    } catch (error) {
      console.error("Failed to sign up with phone:", error)
    }
  }

  return (
    <Box as="form" onSubmit={handleSubmit} width="100%">
      <VStack gap={4}>
        <Field invalid={!!error} errorText={error}>
          <InputGroup startElement={<FiPhone />}>
            <Input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+1 (555) 123-4567"
              type="tel"
              required
            />
          </InputGroup>
        </Field>

        <Field>
          <Input
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Full Name (optional)"
            type="text"
          />
        </Field>

        <Field>
          <Input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            type="password"
            required
          />
        </Field>

        <Button
          type="submit"
          loading={loading}
          disabled={!phone.trim() || !password.trim()}
          width="100%"
          variant="solid"
        >
          Sign Up with Phone
        </Button>
      </VStack>
    </Box>
  )
} 