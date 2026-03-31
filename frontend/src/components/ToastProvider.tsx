import { createContext, useCallback, useContext, useMemo, type ReactNode } from 'react'
import { Toaster, toast } from 'react-hot-toast'

type ToastType = 'success' | 'error' | 'info'

interface ToastContextValue {
  showToast: (message: string, type?: ToastType) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function ToastProvider({ children }: { children: ReactNode }) {
  const showToast = useCallback((message: string, type: ToastType = 'info') => {
    if (type === 'success') {
      toast.success(message)
      return
    }
    if (type === 'error') {
      toast.error(message)
      return
    }
    toast(message)
  }, [])

  const value = useMemo(() => ({ showToast }), [showToast])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <Toaster position="top-right" toastOptions={{ duration: 3000 }} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used inside ToastProvider')
  }
  return context
}
