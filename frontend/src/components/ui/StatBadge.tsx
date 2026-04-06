type Props = {
  label: string
  value: string | number
}

export default function StatBadge({ label, value }: Props) {
  return (
    <div className="stat-badge">
      <div className="stat-badge-label">{label}</div>
      <div className="stat-badge-value">{value}</div>
    </div>
  )
}
