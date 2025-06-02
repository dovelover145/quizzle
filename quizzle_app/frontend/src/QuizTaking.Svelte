<script lang="ts">
  import { onMount } from 'svelte';

  export let quiz: { _id: string; title: string };
  export let onback: () => void;
  export let oncomplete: () => void;

  interface Question {
    id: number;
    question: string;
    options: string[];
    correctAnswer: number;
    explanation: string;
  }

  let questions: Question[] = [];
  let currentQuestionIndex = 0;
  let selectedAnswer: number | null = null;
  let answers: (number | null)[] = [];
  let showResults = false;
  let score = 0;

  onMount(async () => {
    try {
      const res = await fetch('http://localhost:8000/get_questions', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quiz_id: quiz._id })
      });
      console.log('[QuizTaking] get_questions status:', res.status);

      const data = await res.json();
      console.log('[QuizTaking] get_questions data:', data);

      if (res.ok && data.success) {
        questions = data.questions.map((q: any, idx: number) => {
          const opts: string[] = Array.isArray(q.answers) ? q.answers : [];
          const correctIdx = opts.findIndex((s) => s === q.correct_answer);

          return {
            id: idx + 1,
            question: q.question || '(no question)',
            options: opts.length ? opts : ['(no options)'],
            correctAnswer: correctIdx >= 0 ? correctIdx : 0,
            explanation: q.explanation || ''
          };
        });
        answers = new Array(questions.length).fill(null);
        console.log('[QuizTaking] mapped questions:', questions);
      } else {
        console.error('[QuizTaking] get_questions failed:', data.message || res.statusText);
      }
    } catch (err) {
      console.error('[QuizTaking] fetch error:', err);
    }
  });

  function handleAnswerSelect(idx: number) {
    selectedAnswer = idx;
  }
  function handleNext() {
    if (selectedAnswer === null) return;
    const nextAnswers = [...answers];
    nextAnswers[currentQuestionIndex] = selectedAnswer;
    answers = nextAnswers;

    if (currentQuestionIndex < questions.length - 1) {
      currentQuestionIndex += 1;
      selectedAnswer = answers[currentQuestionIndex];
    } else {
      score = questions.reduce((cnt, q, i) => cnt + (answers[i] === q.correctAnswer ? 1 : 0), 0);
      showResults = true;
    }
  }
  function handlePrevious() {
    if (currentQuestionIndex > 0) {
      currentQuestionIndex -= 1;
      selectedAnswer = answers[currentQuestionIndex];
    }
  }
  function handleRestart() {
    currentQuestionIndex = 0;
    selectedAnswer = null;
    answers = new Array(questions.length).fill(null);
    showResults = false;
    score = 0;
  }
  function handleBack() {
    onback();
  }
  function handleComplete() {
    oncomplete();
  }
</script>

<div class="quiz-taking-container">
  <div class="quiz-taking-content">
    {#if questions.length === 0}
      <h2>Loading quiz... (questions.length = {questions.length})</h2>
      <button class="quiz-btn" on:click={handleBack}>
        Back to Quiz
      </button>

    {:else if showResults}
      <div class="results-section">
        <h2 class="results-title">Quiz Complete!</h2>
        <div class="score-display">
          <span class="score-text">Your Score:</span>
          <span class="score-number">{score}/{questions.length}</span>
          <span class="score-percentage">
            ({Math.round((score / questions.length) * 100)}%)
          </span>
        </div>
        <div class="results-breakdown">
          <h3>Review Your Answers:</h3>
          {#each questions as question, idx}
            <div class="result-item">
              <div class="result-question">{question.question}</div>
              <div
                class="result-answer"
                class:correct={answers[idx] === question.correctAnswer}
                class:incorrect={answers[idx] !== question.correctAnswer}
              >
                Your answer: {question.options[answers[idx] || 0]}
                {#if answers[idx] !== question.correctAnswer}
                  <div class="correct-answer">
                    Correct answer: {question.options[question.correctAnswer]}
                  </div>
                  <div class="explanation-text">
                    Explanation: {question.explanation}
                  </div>
                {/if}
              </div>
            </div>
          {/each}
        </div>
        <div class="results-actions">
          <button class="quiz-btn secondary" on:click={handleRestart}>
            Retake Quiz
          </button>
          <button class="quiz-btn" on:click={handleComplete}>
            Back to Quiz Details
          </button>
        </div>
      </div>

    {:else}
      <div class="quiz-header">
        <button class="back-btn" on:click={handleBack}>
          ← Back to Quiz
        </button>
        <div class="progress-info">
          Question {currentQuestionIndex + 1} of {questions.length}
        </div>
      </div>
      <div class="progress-bar">
        <div
          class="progress-fill"
          style="width: {( (currentQuestionIndex + 1) / questions.length) * 100}%;"
        ></div>
      </div>
      <div class="question-section">
        <h2 class="question-title">
          {questions[currentQuestionIndex].question}
        </h2>
        <div class="options-container">
          {#each questions[currentQuestionIndex].options as option, idx}
            <button
              class="option-btn"
              class:selected={selectedAnswer === idx}
              on:click={() => handleAnswerSelect(idx)}
            >
              <span class="option-letter">
                {String.fromCharCode(65 + idx)}
              </span>
              <span class="option-text">{option}</span>
            </button>
          {/each}
        </div>
        <div class="navigation-buttons">
          <button
            class="nav-btn secondary"
            on:click={handlePrevious}
            disabled={currentQuestionIndex === 0}
          >
            Previous
          </button>
          <button
            class="nav-btn"
            on:click={handleNext}
            disabled={selectedAnswer === null}
          >
            {currentQuestionIndex === questions.length - 1
              ? 'Finish Quiz'
              : 'Next'}
          </button>
        </div>
      </div>
    {/if}
  </div>
</div>

  <style>
    .quiz-taking-container {
      min-height: 100vh;
      background: #f5f5f5;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 1000;
    }
  
    .quiz-taking-content {
      background: white;
      border-radius: 12px;
      padding: 2rem;
      max-width: 800px;
      width: 100%;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      max-height: 90vh;
      overflow-y: auto;
    }
  
    .quiz-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }
  
    .back-btn {
      background: none;
      border: 1px solid #e0e0e0;
      padding: 8px 16px;
      border-radius: 6px;
      cursor: pointer;
      color: #666;
      transition: all 0.2s;
    }
  
    .back-btn:hover {
      background: #f8f9fa;
      border-color: #7dd3da;
      color: #7dd3da;
    }
  
    .progress-info {
      font-size: 0.9rem;
      color: #666;
      font-weight: 500;
    }
  
    .progress-bar {
      width: 100%;
      height: 8px;
      background: #e0e0e0;
      border-radius: 4px;
      margin-bottom: 2rem;
      overflow: hidden;
    }
  
    .progress-fill {
      height: 100%;
      background: #7dd3da;
      transition: width 0.3s ease;
    }
  
    .question-section {
      text-align: center;
    }
  
    .question-title {
      font-size: 1.8rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 2rem;
      line-height: 1.4;
    }
  
    .options-container {
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-bottom: 2rem;
    }
  
    .option-btn {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 1rem 1.5rem;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      background: white;
      cursor: pointer;
      transition: all 0.2s;
      text-align: left;
    }
  
    .option-btn:hover {
      border-color: #7dd3da;
      background: #f0fdfe;
    }
  
    .option-btn.selected {
      border-color: #7dd3da;
      background: #7dd3da;
      color: white;
    }
  
    .option-letter {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #f8f9fa;
      font-weight: 600;
      flex-shrink: 0;
    }
  
    .option-btn.selected .option-letter {
      background: rgba(255, 255, 255, 0.2);
      color: white;
    }
  
    .option-text {
      flex: 1;
      font-size: 1rem;
      line-height: 1.4;
    }
  
    .navigation-buttons {
      display: flex;
      gap: 1rem;
      justify-content: center;
    }
  
    .nav-btn {
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
  
    .nav-btn:hover:not(:disabled) {
      background: #6bc5cc;
      transform: translateY(-1px);
    }
  
    .nav-btn:disabled {
      background: #ccc;
      cursor: not-allowed;
      transform: none;
    }
  
    .nav-btn.secondary {
      background: #6c757d;
    }
  
    .nav-btn.secondary:hover:not(:disabled) {
      background: #5a6268;
    }
  
    .results-section {
      text-align: center;
    }
  
    .results-title {
      font-size: 2.5rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 2rem;
    }
  
    .score-display {
      background: #f8f9fa;
      border-radius: 12px;
      padding: 2rem;
      margin-bottom: 2rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0.5rem;
    }
  
    .score-text {
      font-size: 1.2rem;
      color: #666;
    }
  
    .score-number {
      font-size: 3rem;
      font-weight: 700;
      color: #7dd3da;
    }
  
    .score-percentage {
      font-size: 1.1rem;
      color: #666;
    }
  
    .results-breakdown {
      text-align: left;
      margin-bottom: 2rem;
    }
  
    .results-breakdown h3 {
      font-size: 1.3rem;
      margin-bottom: 1rem;
      color: #333;
    }
  
    .result-item {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
    }
  
    .result-question {
      font-weight: 600;
      margin-bottom: 0.5rem;
      color: #333;
    }
  
    .result-answer {
      font-size: 0.9rem;
    }
  
    .result-answer.correct {
      color: #28a745;
    }
  
    .result-answer.incorrect {
      color: #dc3545;
    }
  
    .correct-answer {
      margin-top: 0.25rem;
      color: #28a745;
      font-style: italic;
    }
  
    .results-actions {
      display: flex;
      gap: 1rem;
      justify-content: center;
    }
  
    .quiz-btn {
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
  
    .quiz-btn:hover {
      background: #6bc5cc;
      transform: translateY(-1px);
    }
  
    .quiz-btn.secondary {
      background: #6c757d;
    }
  
    .quiz-btn.secondary:hover {
      background: #5a6268;
    }
  
    @media (max-width: 768px) {
      .quiz-taking-container {
        padding: 1rem;
      }
  
      .quiz-taking-content {
        padding: 1.5rem;
      }
  
      .question-title {
        font-size: 1.5rem;
      }
  
      .navigation-buttons {
        flex-direction: column;
      }
    }
  </style>