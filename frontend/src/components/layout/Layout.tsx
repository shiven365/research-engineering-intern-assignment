import { ReactNode } from 'react'
import Sidebar from './Sidebar'
import TopBar from './TopBar'

type Props = {
  title: string
  children: ReactNode
}

export default function Layout({ title, children }: Props) {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="app-main">
        <TopBar title={title} />
        <div className="app-content">{children}</div>
      </main>
    </div>
  )
}
