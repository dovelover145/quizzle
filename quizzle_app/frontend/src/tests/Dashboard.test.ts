// src/Dashboard.test.ts

import { describe, it, beforeEach, vi, expect } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import Dashboard from '../Dashboard.svelte';

const flushPromises = () => new Promise(resolve => setTimeout(resolve, 0));

describe('Dashboard', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', (url: string, opts?: any) => {
      // 1) user_info
      if (url.endsWith('/user_info')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({ success: true, user: { email: 'user@example.com' } }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          )
        );
      }
      // 2) /get_user_quizzes => one quiz
      if (url.endsWith('/get_user_quizzes')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              success: true,
              public_quizzes: [],
              private_quizzes: [
                {
                  _id: 'quiz1',
                  title: 'My Quiz',
                  date_created: '2025-01-01T00:00:00Z',
                  terms: []
                }
              ]
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          )
        );
      }
      // 3) /get_public_quizzes => one other quiz
      if (url.endsWith('/get_public_quizzes')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({
              success: true,
              public_quizzes: [
                {
                  _id: 'quiz2',
                  title: 'Other Quiz',
                  creator_username: 'alice',
                  date_created: '2025-02-02T00:00:00Z',
                  terms: []
                }
              ]
            }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          )
        );
      }
      return Promise.resolve(new Response(null, { status: 404 }));
    });
  });

  it('renders the home welcome message by default', () => {
    render(Dashboard);
    expect(screen.getByRole('heading', { level: 2, name: 'Welcome to Quizzle' })).toBeInTheDocument();
    expect(
      screen.getByText(
        /Use the menu on the left to "Create," view "My quizzes," or "Study with others' quizzes\./
      )
    ).toBeInTheDocument();
  });

  it('loads and displays only my quizzes when clicking "My quizzes"', async () => {
    render(Dashboard);

    // wait for onMount fetch(user_info) to finish
    await flushPromises();

    // now click the sidebar item
    await fireEvent.click(screen.getByText('My quizzes'));

    // Section heading appears
    expect(await screen.findByText('My recent quizzes')).toBeInTheDocument();

    // Our stubbed quiz card title shows as an <h3>
    expect(await screen.findByRole('heading', { level: 3, name: 'My Quiz' })).toBeInTheDocument();

    expect(screen.getByText(/2024/)).toBeInTheDocument();

    // It should render exactly one card
    const cards = screen.getAllByRole('heading', { level: 3 });
    expect(cards).toHaveLength(1);
  });

  it("loads and displays others' public quizzes when clicking \"Study with others' quizzes\"", async () => {
    render(Dashboard);

    await fireEvent.click(screen.getByText("Study with others' quizzes"));

    expect(
      await screen.findByRole('heading', { level: 2, name: "Study with others' quizzes" })
    ).toBeInTheDocument();

    expect(await screen.findByRole('heading', { level: 3, name: 'Other Quiz' })).toBeInTheDocument();
    expect(screen.getByText('by alice')).toBeInTheDocument();
  });
});
