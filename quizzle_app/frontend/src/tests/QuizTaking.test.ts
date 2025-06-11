import { describe, it, beforeEach, expect, vi } from 'vitest';
import { render, fireEvent, screen } from '@testing-library/svelte';
import QuizTaking from '../QuizTaking.svelte';

describe('QuizTaking', () => {
  const dummyQuestions = [
    { _id: 'q1', question: 'What is 2+2?', answers: ['4', '3'], correct_answer: '4', explanation: 'Basic math' },
    { _id: 'q2', question: 'Capital of CA?', answers: ['Sac', 'LA'], correct_answer: 'Sac', explanation: 'Capital city' }
  ];

  let fetchMock: any;

  beforeEach(() => {
    fetchMock = vi.fn((url: string) => {
      if (url.endsWith('/get_all_questions')) {
        return Promise.resolve(new Response(
          JSON.stringify({ success: true, questions: dummyQuestions }),
          { status: 200, headers: { 'Content-Type': 'application/json' } }
        ));
      }
      if (url.endsWith('/get_questions')) {
        return Promise.resolve(new Response(
          JSON.stringify({ success: true, questions: [dummyQuestions[0]] }),
          { status: 200, headers: { 'Content-Type': 'application/json' } }
        ));
      }
      return Promise.resolve(new Response(null, { status: 404 }));
    });
    vi.stubGlobal('fetch', fetchMock);
  });

  it('loads and displays the first question and its correct answer button', async () => {
    const oncomplete = vi.fn();
    render(QuizTaking, {
      props: {
        quiz: { _id: 'quiz1', title: 'Test Quiz' },
        back: () => {},
        oncomplete
      }
    });

    // Should show loading initially
    expect(screen.getByText(/Loading quiz/i)).toBeInTheDocument();

    // After fetch, question appears
    expect(await screen.findByText('What is 2+2?')).toBeInTheDocument();

    // Only assert presence of correct answer '4'
    const answer4Span = await screen.findByText('4');
    const btn4 = answer4Span.closest('button');
    expect(btn4).toBeInTheDocument();
  });

  it('marks the selected answer and completes the quiz', async () => {
    const oncomplete = vi.fn();
    render(QuizTaking, {
        props: {
        quiz: { _id: 'quiz1', title: 'Test Quiz' },
        back: () => {},
        oncomplete
        }
    });

    // Pick the correct answer
    const btn4 = (await screen.findByText('4')).closest('button')!;
    await fireEvent.click(btn4);
    expect(btn4).toHaveClass('selected');

    // Click Finish Quiz to reveal the results screen
    const finishBtn = screen.getByRole('button', { name: /Finish Quiz/i });
    await fireEvent.click(finishBtn);

    // Wait for the results heading, then click "Back to Quiz Details"
    expect(await screen.findByText('Quiz Complete!')).toBeInTheDocument();
    const backBtn = await screen.findByRole('button', { name: /Back to Quiz Details/i });
    await fireEvent.click(backBtn);

    // Now oncomplete should have been called
    expect(oncomplete).toHaveBeenCalled();
    });

});
