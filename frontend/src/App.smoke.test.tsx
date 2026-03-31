import { describe, expect, it } from 'vitest'
import { renderToString } from 'react-dom/server'
import { StaticRouter } from 'react-router-dom/server'
import { Sidebar } from './components/Sidebar'

describe('Frontend smoke', () => {
  it('renders dashboard navigation', () => {
    const html = renderToString(
      <StaticRouter location="/">
        <Sidebar />
      </StaticRouter>,
    )

    expect(html).toContain('Dashboard')
    expect(html).toContain('Projects')
  })
})
