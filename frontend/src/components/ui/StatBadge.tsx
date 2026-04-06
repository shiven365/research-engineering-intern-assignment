type Props = {
  label: string
  value: string | number
}

export default function StatBadge({ label, value }: Props) {
  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderRadius: 10,
        padding: 14,
        background: 'linear-gradient(180deg, rgba(17,29,51,0.95) 0%, rgba(14,24,43,0.95) 100%)',
      }}
    >
      <div style={{ fontSize: 12, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
        {label}
      </div>
      <div style={{ fontSize: 24, fontFamily: 'var(--font-data)', color: 'var(--accent-secondary)' }}>{value}</div>
    </div>
  )
}
