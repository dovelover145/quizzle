import { render, fireEvent, screen } from '@testing-library/svelte';
import { vi } from 'vitest';
import EditQuiz from '../EditQuiz.svelte';

describe('EditQuiz', () => {
  const dummyId = 'test123';

  beforeEach(() => {
    // stub fetch for user_info, get_user_quizzes, get_questions…
    interface UserInfoResponse {
      success: boolean;
      user: {
        email: string;
      };
    }

    interface Quiz {
      _id: string;
      title: string;
      is_public: boolean;
      description: string;
      date_created: string;
    }

    interface GetUserQuizzesResponse {
      success: boolean;
      public_quizzes: Quiz[];
      private_quizzes: Quiz[];
    }

    interface GetQuestionsResponse {
      success: boolean;
      questions: any[]; // Replace 'any' with a specific Question interface if available
    }

    vi.stubGlobal('fetch', (url: string, opts?: RequestInit): Promise<Response> => {
      // simple stub: return success shapes based on URL
      if (url.endsWith('/user_info')) {
        const body: UserInfoResponse = { success: true, user: { email: 'a@b' } };
        return Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));
      }
      if (url.endsWith('/get_user_quizzes')) {
        const body: GetUserQuizzesResponse = {
          success: true,
          public_quizzes: [],
          private_quizzes: [{
            _id: dummyId,
            title: '',
            is_public: true,
            description: '',
            date_created: ''
          }]
        };
        return Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));
      }
      if (url.endsWith('/get_questions')) {
        const body: GetQuestionsResponse = { success: true, questions: [] };
        return Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));
      }
      // fallback
      return Promise.resolve(new Response(null, { status: 404 }));
    });
  });

  it('shows title input and update button', async () => {
    render(EditQuiz, { props: { quizId: dummyId } });

    // wait for the input to show up
    const titleInput = await screen.findByPlaceholderText('Enter title...');
    expect(titleInput).toBeInTheDocument();

    const updateBtn = await screen.findByRole('button', { name: /Update/i });
    expect(updateBtn).toBeInTheDocument();
  });

  it('alerts if title is empty on update', async () => {
    render(EditQuiz, { props: { quizId: dummyId } });

    // wait for the Update button to mount
    const updateBtn = await screen.findByRole('button', { name: /Update/i });

    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
    await fireEvent.click(updateBtn);
    expect(alertSpy).toHaveBeenCalledWith('Enter a quiz title');
    alertSpy.mockRestore();
  });
});
