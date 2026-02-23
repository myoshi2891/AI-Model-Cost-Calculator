import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders correctly', () => {
    render(<App />)
    // Check for some text from Hero or App
    expect(screen.getByText(/AI Cost Simulator/i)).toBeInTheDocument()
    expect(screen.getAllByText(/USD \+ JPY/i).length).toBeGreaterThan(0)
  })
})
