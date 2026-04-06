type Props = {
  height?: number
}

export default function Skeleton({ height = 120 }: Props) {
  return <div className="skeleton" style={{ height }} />
}
