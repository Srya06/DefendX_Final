import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import Home from '../src/app/page'

test('Home page renders successfully', () => {
  render(<Home />)
  // Check if main element is present
  const mainElement = screen.getByRole('main')
  expect(mainElement).toBeDefined()
})
