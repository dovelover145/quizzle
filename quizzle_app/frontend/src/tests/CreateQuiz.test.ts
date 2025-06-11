import { describe, it, beforeEach, expect, vi } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import CreateQuiz from '../CreateQuiz.svelte';

describe('CreateQuiz', () => {
  let fetchMock: any;

  beforeEach(() => {
    // create a jest‐like mock function
    fetchMock = vi.fn((url, opts) => {
      if (url.endsWith('/user_info')) {
        return Promise.resolve(new Response(
          JSON.stringify({ success: true, user: { email: 'test@user' } }),
          { status: 200, headers: { 'Content-Type': 'application/json' } }
        ));
      }
      if (url.endsWith('/create_quiz')) {
        return Promise.resolve(new Response(
          JSON.stringify({ success: true, quiz_id: 'new123' }),
          { status: 200, headers: { 'Content-Type': 'application/json' } }
        ));
      }
      return Promise.resolve(new Response(null, { status: 404 }));
    });

    // override the global fetch with our mock
    vi.stubGlobal('fetch', fetchMock);
  });

  it('submits payload when clicking Create', async () => {
    render(CreateQuiz);

    // fill fields
    await fireEvent.input(screen.getByPlaceholderText('Enter title...'), { target: { value: 'My Quiz' } });
    await fireEvent.input(screen.getByPlaceholderText('Enter term'), { target: { value: 'Term1' } });
    await fireEvent.input(screen.getByPlaceholderText('Enter description'), { target: { value: 'Desc1' } });

    // click Create
    const createBtn = screen.getByText('Create');
    await fireEvent.click(createBtn);

    // ensure fetch was called at least once
    expect(fetchMock).toHaveBeenCalled();

    // find the call for /create_quiz
    const call = fetchMock.mock.calls.find(([url]) => url.endsWith('/create_quiz'));
    expect(call).toBeTruthy();

    const [, opts] = call!;
    const body = JSON.parse((opts as RequestInit).body as string);
    expect(body.title).toBe('My Quiz');
    expect(body.quiz_id).toBeUndefined();       // you don't send quiz_id when creating
    expect(body.creator_username).toBe('test@user');
  });
});
