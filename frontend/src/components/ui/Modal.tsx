import { Dialog, DialogPanel, DialogTitle } from '@headlessui/react'
import type { PropsWithChildren, ReactNode } from 'react'

interface ModalProps extends PropsWithChildren {
  isOpen: boolean
  title: string
  onClose: () => void
  footer?: ReactNode
}

export function Modal({ isOpen, title, onClose, footer, children }: ModalProps) {
  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-slate-900/50" aria-hidden="true" />
      <div className="fixed inset-0 overflow-y-auto p-4">
        <div className="flex min-h-full items-center justify-center">
          <DialogPanel className="w-full max-w-xl rounded-2xl bg-white p-6 shadow-xl">
            <DialogTitle className="text-lg font-semibold text-slate-900">{title}</DialogTitle>
            <div className="mt-4 space-y-4">{children}</div>
            {footer ? <div className="mt-5 flex justify-end gap-2">{footer}</div> : null}
          </DialogPanel>
        </div>
      </div>
    </Dialog>
  )
}
