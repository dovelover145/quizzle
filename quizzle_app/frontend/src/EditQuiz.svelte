<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();
  export let quizId: string;

  let userEmail = '';
  let quizTitle = '';
  let isPublic = true;
  let loading = true;
  let error = '';
  let quizDescription = '';
  let dateCreated = '';

  interface TermItem { id: number; term: string; description: string; questionId?: string; }

  let terms: TermItem[] = [];
  let nextTermId = 1;
  let originalQuestions: { _id: string; question: string; correct_answer: string }[] = [];

  onMount(async () => {
    try {
      const userRes = await fetch('http://localhost:8000/user_info', { credentials: 'include' });
      const userData = await userRes.json();
      userEmail = userRes.ok && userData.success ? userData.user.email : '';
      await loadQuizData();
    } catch (err) {
      console.error('Init EditQuiz error:', err);
      error = 'Failed to load quiz data';
    } finally {
      loading = false;
    }
  });

  async function loadQuizData() {
    try {
      const quizzesRes = await fetch('http://localhost:8000/get_user_quizzes', {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ creator_username: userEmail })
      });
      if (!quizzesRes.ok) throw new Error('Failed to fetch quizzes');
      const { success, public_quizzes, private_quizzes, message } = await quizzesRes.json();
      if (!success) throw new Error(message || 'Could not load quizzes');
      const allQuizzes = [...public_quizzes, ...private_quizzes];
      const quiz = allQuizzes.find(q => q._id === quizId);
      if (!quiz) throw new Error('Quiz not found');
      quizTitle = quiz.title || '';
      isPublic = quiz.is_public;
      quizDescription = quiz.description || '';
      dateCreated = quiz.date_created;
      const questionsRes = await fetch('http://localhost:8000/get_questions', {
        method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quiz_id: quizId })
      });
      if (!questionsRes.ok) throw new Error('Failed to fetch questions');
      const { success: qSuccess, questions, message: qMsg } = await questionsRes.json();
      if (!qSuccess) throw new Error(qMsg || 'Could not load questions');
      originalQuestions = questions;
      terms = questions.map((q, i) => ({ id: i+1, term: q.question||'', description: q.correct_answer||'', questionId: q._id }));
      nextTermId = terms.length + 1;
    } catch (err) {
      console.error('loadQuizData error:', err);
      error = 'Failed to load quiz data';
      terms = [{ id:1, term:'', description:'' }]; nextTermId = 2;
    }
  }

  function addTerm() { terms = [...terms, { id: nextTermId, term:'', description:'' }]; nextTermId++; }
  function removeTerm(id: number) { if(terms.length>1) terms = terms.filter(t => t.id!==id); }
  function updateTerm(id:number, field:'term'|'description', val:string) { terms = terms.map(t=>t.id===id?{...t,[field]:val}:t); }
  function toggleVisibility() { isPublic = !isPublic; }

  async function handleUpdate() {
    if(!quizTitle.trim()){ alert('Enter a quiz title'); return; }
    if(!userEmail){ alert('Login required'); return; }
    try {
      const resMeta = await fetch('http://localhost:8000/update_quiz', {
        method:'POST', credentials:'include', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({_id:quizId,title:quizTitle,description:quizDescription,creator_username:userEmail,is_public:isPublic,date_created:dateCreated})
      });
      if(!resMeta.ok){ const e=await resMeta.json(); throw new Error(e.message||'Meta update failed'); }
      const origMap = new Map(originalQuestions.map(q=>[q._id,q]));
      for(const t of terms){
        if(!t.term.trim()||!t.description.trim()) continue;
        if(t.questionId){
          const orig=origMap.get(t.questionId)!;
          if(orig.question!==t.term||orig.correct_answer!==t.description){
            await fetch('http://localhost:8000/add_question',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({quiz_id:quizId,question:t.term,answers:[t.description],correct_answer:t.description,explanation:''})});
            // delete old question by sending {_id: t.questionId}
            await fetch('http://localhost:8000/delete_question',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({_id:t.questionId})});
          }
          origMap.delete(t.questionId);
        } else {
          await fetch('http://localhost:8000/add_question',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({quiz_id:quizId,question:t.term,answers:[t.description],correct_answer:t.description,explanation:''})});
        }
      }
      for(const oldId of origMap.keys()){
        await fetch('http://localhost:8000/delete_question',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({_id:oldId})});
      }
      dispatch('updated',{_id:quizId,title:quizTitle,is_public:isPublic}); alert('Quiz updated successfully!');
    } catch(err){ console.error('update error:',err); alert('Failed to update quiz: '+(err as Error).message); }
  }
  
  function handleCancel(){ dispatch('close'); }

  async function handleDelete() {
    if (!confirm('Are you sure you want to delete this quiz? This action cannot be undone.')) {
      return;
    }

    try {
      // 1) hit your delete_quiz endpoint
      const res = await fetch('http://localhost:8000/delete_quiz', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ _id: quizId })
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.message || 'Server rejected delete');
      }

      // 2) notify parent & clear out UI
      dispatch('deleted', { _id: quizId });
      alert('Quiz deleted successfully!');
    } catch (err) {
      console.error('Error deleting quiz:', err);
      alert('Failed to delete quiz: ' + (err as Error).message);
    }
  }


</script>


{#if loading}
  <div class="loading-container">
    <div class="loading-spinner"></div>
    <p>Loading quiz data...</p>
  </div>
{:else if error}
  <div class="error-container">
    <p class="error-message">{error}</p>
    <button class="retry-btn" on:click={loadQuizData}>Retry</button>
    <button class="cancel-btn" on:click={handleCancel}>Cancel</button>
  </div>
{:else}
  <div class="dashboard-container">
    <main class="main-content">
      <div class="create-header">
        <h1 class="page-title">Edit quiz</h1>
        <div class="header-actions">
          <button class="cancel-btn" on:click={handleCancel}>Cancel</button>
          <button class="delete-btn" on:click={handleDelete}>
            Delete
          </button>
          <button class="create-btn" on:click={handleUpdate}>Update</button>
        </div>
      </div>

      <div class="form-container">
        <class class="form-section">
          <label class="form-label" for="quiz-title">Title</label>
          <input
            id="quiz-title"
            type="text"
            class="form-input"
            placeholder="Enter title..."
            bind:value={quizTitle}
          />
        </class>

        <div class="form-section">
          <div class="visibility-section">
            <label class="form-label">Quiz Visibility</label>
            <div class="toggle-container">
              <span class="toggle-label" class:active={!isPublic}>Private</span>
              <button class="toggle-switch" class:public={isPublic} on:click={toggleVisibility}>
                <div class="toggle-slider"></div>
              </button>
              <span class="toggle-label" class:active={isPublic}>Public</span>
            </div>
            <p class="visibility-description">
              {isPublic
                ? 'Other users can find and study with your quiz'
                : 'Only you can access this quiz'}
            </p>
          </div>
        </div>

        <div class="form-section">
          <label class="form-label">Terms</label>
          <div class="terms-container">
            {#each terms as term, index}
              <div class="term-card">
                <div class="term-header">
                  <span class="term-number">{index + 1}</span>
                  {#if terms.length > 1}
                    <button class="delete-btn" on:click={() => removeTerm(term.id)}>
                      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M3 6h18"></path>
                        <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                        <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                      </svg>
                    </button>
                  {/if}
                </div>
                <div class="term-inputs">
                  <input
                    type="text"
                    class="form-input"
                    placeholder="Enter term"
                    value={term.term}
                    on:input={(e) => updateTerm(term.id, 'term', e.target.value)}
                  />
                  <textarea
                    class="form-textarea"
                    placeholder="Enter description"
                    value={term.description}
                    on:input={(e) => updateTerm(term.id, 'description', e.target.value)}
                  ></textarea>
                </div>
              </div>
            {/each}

            <button class="add-term-btn" on:click={addTerm}>
              <span class="icon">+</span> Add a term
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
{/if}


  
  <style>
    .dashboard-container {
      display: flex;
      min-height: 100vh;
    }
  
    .main-content {
      flex: 1;
      padding: 2rem 3rem;
      min-width: 0;
      max-width: 800px;
    }
  
    .create-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
    }
  
    .header-actions {
      display: flex;
      gap: 1rem;
      align-items: center;
    }
  
    .page-title {
      font-size: 2rem;
      font-weight: 600;
      color: #333;
      margin: 0;
    }
  
    .create-btn {
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
  
    .create-btn:hover {
      background: #6bc5cc;
      transform: translateY(-1px);
    }
  
    .cancel-btn {
      background: #f8f9fa;
      color: #666;
      border: 2px solid #e0e0e0;
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
    }
  
    .cancel-btn:hover {
      background: #e9ecef;
      border-color: #d0d0d0;
      color: #333;
    }
  
    .form-container {
      display: flex;
      flex-direction: column;
      gap: 2rem;
    }
  
    .form-section {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }
  
    .form-label {
      font-size: 1.1rem;
      font-weight: 600;
      color: #333;
    }
  
    .form-input {
      padding: 12px 16px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      font-size: 1rem;
      transition: border-color 0.2s;
      background: #f8f9fa;
    }
  
    .form-input:focus {
      outline: none;
      border-color: #7dd3da;
      background: white;
    }
  
    .form-textarea {
      padding: 12px 16px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      font-size: 1rem;
      min-height: 80px;
      resize: vertical;
      font-family: inherit;
      transition: border-color 0.2s;
      background: #f8f9fa;
    }
  
    .form-textarea:focus {
      outline: none;
      border-color: #7dd3da;
      background: white;
    }
  
    .visibility-section {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
  
    .toggle-container {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
  
    .toggle-label {
      font-size: 0.95rem;
      color: #666;
      font-weight: 500;
      transition: color 0.2s;
    }
  
    .toggle-label.active {
      color: #333;
      font-weight: 600;
    }
  
    .toggle-switch {
      position: relative;
      width: 50px;
      height: 26px;
      background: #ccc;
      border: none;
      border-radius: 26px;
      cursor: pointer;
      transition: background-color 0.3s;
      padding: 0;
    }
  
    .toggle-switch.public {
      background: #7dd3da;
    }
  
    .toggle-slider {
      position: absolute;
      top: 2px;
      left: 2px;
      width: 22px;
      height: 22px;
      background: white;
      border-radius: 50%;
      transition: transform 0.3s;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
  
    .toggle-switch.public .toggle-slider {
      transform: translateX(24px);
    }
  
    .visibility-description {
      font-size: 0.9rem;
      color: #666;
      margin: 0;
      font-style: italic;
    }
  
    .terms-container {
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }
  
    .term-card {
      border: 2px solid #e0e0e0;
      border-radius: 12px;
      padding: 1.5rem;
      background: #fafbfc;
      transition: border-color 0.2s;
    }
  
    .term-card:focus-within {
      border-color: #7dd3da;
      background: white;
    }
  
    .term-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }
  
    .term-number {
      font-weight: 600;
      color: #333;
      font-size: 1.1rem;
    }
  
    .delete-btn {
      background: none;
      border: none;
      color: #dc3545;
      cursor: pointer;
      padding: 6px;
      border-radius: 4px;
      transition: background-color 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  
    .delete-btn:hover {
      background: #fff5f5;
    }
  
    .term-inputs {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
  
    .add-term-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      padding: 1rem;
      border: 2px dashed #ccc;
      border-radius: 12px;
      background: none;
      color: #666;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
    }
  
    .add-term-btn:hover {
      border-color: #7dd3da;
      color: #7dd3da;
      background: #f0fdfe;
    }
  
    .add-term-btn .icon {
      font-size: 1.2rem;
      font-weight: 300;
    }
  
    .loading-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 400px;
      gap: 1rem;
    }
  
    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 4px solid #f3f3f3;
      border-top: 4px solid #7dd3da;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
  
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  
    .error-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 400px;
      gap: 1rem;
    }
  
    .error-message {
      color: #dc3545;
      font-size: 1.1rem;
      text-align: center;
    }
  
    .retry-btn {
      background: #7dd3da;
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.2s;
    }
  
    .retry-btn:hover {
      background: #6bc5cc;
    }
    .delete-btn {
      background: none;
      border: none;
      color: #dc3545;
      cursor: pointer;
      padding: 6px;
      border-radius: 4px;
      transition: background-color 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  
    .delete-btn:hover {
      background: #fff5f5;
    }
  
    @media (max-width: 768px) {
      .main-content {
        padding: 1.5rem;
      }
      
      .create-header {
        flex-direction: column;
        gap: 1rem;
        align-items: flex-start;
      }
      
      .page-title {
        font-size: 1.75rem;
      }
      
      .toggle-container {
        flex-wrap: wrap;
        gap: 0.75rem;
      }
  
      .header-actions {
        align-self: stretch;
        justify-content: flex-end;
      }
    }
  </style>