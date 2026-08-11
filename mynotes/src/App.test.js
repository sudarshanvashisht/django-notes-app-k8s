import { render, screen, waitFor } from '@testing-library/react';
import App from './App';

describe('App', () => {
  beforeEach(() => {
    global.fetch = jest.fn((url) => {
      if (url.includes('/api/notes/')) {
        return Promise.resolve({
          json: () => Promise.resolve([]),
        });
      }

      return Promise.resolve({
        json: () => Promise.resolve({}),
      });
    });
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('renders the dashboard shell', async () => {
    render(<App />);

    expect(screen.getByRole('heading', { name: /notes ops/i })).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/no notes yet/i)).toBeInTheDocument();
    });
  });
});
