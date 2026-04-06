import { ReactNode } from 'react'
import Sidebar from './Sidebar'
import TopBar from './TopBar'

type Props = {
  title: string
  children: ReactNode
}

export default function Layout({ title, children }: Props) {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{ marginLeft: 240, width: 'calc(100% - 240px)' }}>
        <TopBar title={title} />
        <div style={{ padding: 18 }}>{children}</div>
      </main>
    </div>
  )
}
