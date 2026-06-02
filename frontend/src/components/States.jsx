export function Loading({ label = 'Loading…' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-industrial-muted">
      <div className="w-10 h-10 border-2 border-industrial-border border-t-industrial-cyan rounded-full animate-spin" />
      <p className="mt-3 text-sm">{label}</p>
    </div>
  )
}

export function ErrorBox({ message }) {
  return (
    <div className="card p-6 border-industrial-red/40 text-industrial-red animate-fade-in">
      <div className="font-medium mb-1">Unable to load data</div>
      <p className="text-sm text-industrial-muted">{message}</p>
      <p className="text-xs text-industrial-muted mt-2">
        Tip: generate data and train models, then run{' '}
        <code className="text-industrial-cyan">python -m backend.ml.batch_predict</code>.
      </p>
    </div>
  )
}
