import { ReactNode } from 'react'

type Props = {
  children: ReactNode
  className?: string
}

export default function Card({ children, className }: Props) {
  return <section className={`card ${className || ''}`}>{children}</section>
}
