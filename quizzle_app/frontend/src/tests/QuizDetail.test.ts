// src/QuizDetail.spec.ts
import { describe, it, beforeEach, expect, vi } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import QuizDetail from '../QuizDetail.svelte';

describe('QuizDetail', () => {
  const dummyQuiz = { _id: 'quiz123', title: 'Sample Quiz' };
  const dummyQuestions = [
    { _id: 'q1', question: 'Q1?', answers: ['A1'], correct_answer: 'A1', explanation: 'Expl1' },
    { _id: 'q2', question: 'Q2?', answers: ['A2'], correct_answer: 'A2', explanation: 'Expl2' }
  ];

  let fetchMock: any;

  beforeEach(() => {
    fetchMock = vi.fn((url: string, opts: any) => {
      // 1) QuizDetail calls POST /get_questions
      if (url.endsWith('/get_questions')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({ success: true, questions: dummyQuestions }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          )
        );
      }
      // 2) QuizTaking calls GET /get_all_questions
      if (url.endsWith('/get_all_questions')) {
        return Promise.resolve(
          new Response(
            JSON.stringify({ success: true, questions: dummyQuestions }),
            { status: 200, headers: { 'Content-Type': 'application/json' } }
          )
        );
      }
      // fallback 404
      return Promise.resolve(new Response(null, { status: 404 }));
    });

    vi.stubGlobal('fetch', fetchMock);
  });

  it('renders quiz title and initial questions', async () => {
    render(QuizDetail, {
      props: {
        quiz: dummyQuiz,
        back: () => {},
        complete: () => {}
      }
    });

    // wait for title
    expect(await screen.findByText(dummyQuiz.title)).toBeInTheDocument();
    // QuizDetail shows explanation text immediately
    expect(await screen.findByText('Expl1')).toBeInTheDocument();
  });

  it('lets user click “Take quiz” and then shows question text', async () => {
    render(QuizDetail, {
      props: {
        quiz: dummyQuiz,
        back: () => {},
        complete: () => {}
      }
    });

    // wait for the Take quiz button to appear
    const takeBtn = await screen.findByRole('button', { name: /Take quiz/i });
    await fireEvent.click(takeBtn);

    // after clicking, QuizTaking mounts and fetches both endpoints,
    // so we should now see the first question
    expect(await screen.findByText('Q1?')).toBeInTheDocument();
  });
});
