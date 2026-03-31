import React from 'react'

interface AppErrorBoundaryProps {
  children: React.ReactNode
}

interface AppErrorBoundaryState {
  hasError: boolean
  errorMessage: string
}

export class AppErrorBoundary extends React.Component<AppErrorBoundaryProps, AppErrorBoundaryState> {
  constructor(props: AppErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, errorMessage: '' }
  }

  static getDerivedStateFromError(error: Error): AppErrorBoundaryState {
    return { hasError: true, errorMessage: error.message }
  }

  componentDidCatch(error: Error) {
    console.error('App runtime error:', error)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
          <div className="w-full max-w-2xl rounded-xl border border-rose-200 bg-white p-6 shadow-sm">
            <h1 className="text-xl font-semibold text-rose-700">Frontend runtime error</h1>
            <p className="mt-2 text-sm text-slate-700">
              The app crashed while rendering. Open DevTools Console to see details.
            </p>
            <p className="mt-3 rounded-md bg-slate-100 p-3 text-xs text-slate-700">{this.state.errorMessage}</p>
            <button
              type="button"
              className="mt-4 rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white"
              onClick={() => window.location.reload()}
            >
              Reload page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
