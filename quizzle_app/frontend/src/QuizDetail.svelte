<script lang="ts">
    import QuizTaking from './QuizTaking.svelte';
  
  
    interface Props {
      quiz: {
      _id: string;
      title: string;
      date_created?: string;
      creator_username?: string;
      terms?: Array<{ term: string; description: string }>;
    };
      back: () => void;
      complete: () => void;
    }
  
    let { quiz, back, complete }: Props = $props();
  
    let showQuizTaking = false;
  
    function handleBack() {
      back();
    }
  
    function handleTakeQuiz() {
      showQuizTaking = true;
    }
  
    function handleQuizComplete() {
      showQuizTaking = false;
      complete();
    }
  
    function handleQuizBack() {
      showQuizTaking = false;
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
        {#if quiz.terms && quiz.terms.length > 0}
          {#each quiz.terms as term, index}
            <div class="term-display-card">
              <h3 class="term-display-title">Term {index + 1}</h3>
              <div class="term-display-content">
                <h4 class="term-name">{term.term}</h4>
                <p class="term-definition">{term.description}</p>
              </div>
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
  