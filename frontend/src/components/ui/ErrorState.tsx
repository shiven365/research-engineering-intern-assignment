type Props = {
  message: string
}

export default function ErrorState({ message }: Props) {
  return (
    <div
      style={{
        border: '1px solid var(--danger)',
        background: 'rgba(255,51,102,0.08)',
        color: 'var(--text-primary)',
        borderRadius: 8,
        padding: 14,
      }}
    >
      {message}
    </div>
  )
}
