<script lang="ts">
  import { onMount } from 'svelte';
  import QuizTaking from './QuizTaking.svelte';

  export let quiz: {
    _id: string;
    title: string;
  };
  export let back: () => void;
  export let complete: () => void;

  let terms: Array<{ term: string; description: string }> = [];

  let showQuizTaking = false;

  onMount(async () => {
    try {
      const res = await fetch('http://localhost:8000/get_questions', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quiz_id: quiz._id })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        terms = data.questions.map((q: any) => ({
          term: q.question,
          description: q.explanation
        }));
      } else {
        console.error('fetch failed:', data.message || res.statusText);
      }
    } catch (e) {
      console.error('fetch error:', e);
    }
  });

  function handleTakeQuiz() {
    showQuizTaking = true;
  }
  function handleQuizBack() {
    showQuizTaking = false;
  }
  function handleQuizComplete() {
    showQuizTaking = false;
    complete();
  }
  function handleBack() {
    back();
  }
</script>
  
  {#if showQuizTaking}
    <QuizTaking 
      {quiz} 
      oncomplete={handleQuizComplete}
      onback={handleQuizBack}
    />
  {:else}
    <div class="quiz-detail-container">
      <div class="quiz-detail-header">
        <h1 class="quiz-detail-title">{quiz.title}</h1>
        <button class="take-quiz-btn" onclick={handleTakeQuiz}>
          Take quiz
        </button>
      </div>
  
      <div class="terms-display">
        {#if terms.length > 0}
          {#each terms as t}
            <div class="term-card">
              <h3>{t.term}</h3>
              <p>{t.description}</p>
            </div>
          {/each}
        {:else}
          <p>No terms available for this quiz.</p>
        {/if}
      </div>
    </div>
  {/if}
  
  <style>
    .quiz-detail-container {
      max-width: 800px;
      margin: 0 auto;
    }
  
    .quiz-detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      padding-bottom: 1rem;
      border-bottom: 2px solid #e0e0e0;
    }
  
    .quiz-detail-title {
      font-size: 2.5rem;
      font-weight: 600;
      color: #333;
      margin: 0;
    }
  
    .take-quiz-btn {
      background: #7dd3da;
      color: white;
      border: none;
      padding: 12px 24px;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }
  
    .take-quiz-btn:hover {
      background: #6bc5cc;
      transform: translateY(-1px);
    }
  
    .terms-display {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
  
    .term-display-card {
      border: 2px solid #e0e0e0;
      border-radius: 12px;
      padding: 1.5rem;
      background: white;
      transition: border-color 0.2s;
    }
  
    .term-display-card:hover {
      border-color: #7dd3da;
    }
  
    .term-display-title {
      font-size: 1.2rem;
      font-weight: 600;
      color: #666;
      margin: 0 0 1rem 0;
    }
  
    .term-display-content {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }
  
    .term-name {
      font-size: 1.3rem;
      font-weight: 600;
      color: #333;
      margin: 0;
    }
  
    .term-definition {
      font-size: 1rem;
      color: #555;
      line-height: 1.5;
      margin: 0;
    }
  
    @media (max-width: 768px) {
      .quiz-detail-header {
        flex-direction: column;
        gap: 1rem;
        align-items: flex-start;
      }
      
      .quiz-detail-title {
        font-size: 2rem;
      }
    }
  </style>
  