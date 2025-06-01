<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  let userEmail: string = '';
  let quizTitle: string = '';
  let isPublic: boolean = true;

  interface TermItem {
    id: number;
    term: string;
    description: string;
  }


  let terms: TermItem[] = [
    { id: 1, term: '', description: '' }
  ];
  let nextTermId = 2;


  function addTerm() {
    terms = [
      ...terms,
      { id: nextTermId, term: '', description: '' }
    ];
    nextTermId += 1;
  }


  function removeTerm(id: number) {
    if (terms.length > 1) {
      terms = terms.filter(term => term.id !== id);
    }
  }

  function updateTerm(id: number, field: 'term' | 'description', value: string) {
    terms = terms.map((t) => {
      if (t.id === id) {
        return { ...t, [field]: value };
      }
      return t;
    });
  }

  function toggleVisibility() {
    isPublic = !isPublic;
  }

  onMount(async () => {
    try {
      const res = await fetch('http://localhost:8000/user_info', {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok && data.success) {
        userEmail = data.user.email;
      } else {
        userEmail = '';
      }
    } catch (err) {
      console.error('Failed to fetch user_info:', err);
      userEmail = '';
    }
  });

  async function handleCreate() {
    if (!quizTitle.trim()) {
      alert('Enter a quiz title');
      return;
    }
    if (!userEmail) {
      alert('You must be logged in to create a quiz');
      return;
    }

    const payload = {
      title: quizTitle,
      description: '',
      creator_username: userEmail,
      is_public: isPublic,
      // if needed, send  a terms here too
      // terms: terms.filter(t => t.term.trim() && t.description.trim())
    };

    try {
      const res = await fetch('http://localhost:8000/create_quiz', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) {
        alert('Failed to create quiz: ' + (data.message || res.statusText));
        return;
      }
      console.log('Quiz created:', data.quiz);
      dispatch('created', data.quiz);

      quizTitle = '';
      isPublic = true;
      terms = [{ id: 1, term: '', description: '' }];
      nextTermId = 2;
    } catch (err) {
      console.error('create_quiz call error:', err);
      alert('Network error while creating quiz');
    }
  }

  function handleCancel() {
    dispatch('close');
  }
</script>


  
  <div class="dashboard-container">
    <main class="main-content">
      <div class="create-header">
        <h1 class="page-title">Create a new quiz</h1>
        <button class="create-btn" on:click={handleCreate}>
          Create
        </button>
      </div>
  
      <div class="form-container">
        <div class="form-section">
          <label class="form-label" for="quiz-title">Title</label>
          <input
            id="quiz-title"
            type="text"
            class="form-input"
            placeholder="Enter title..."
            bind:value={quizTitle}
          />
        </div>
  
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
              {isPublic ? 'Other users can find and study with your quiz' : 'Only you can access this quiz'}
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
              <span class="icon">+</span>
              Add a term
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
  
  <style>
    .dashboard-container {
      display: flex;
      min-height: 100vh;
    }
  
    .sidebar {
      width: 290px;
      background-color: #e8f4f6;
      padding: 2rem 0;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }
  
    .sidebar-item {
      display: flex;
      align-items: center;
      padding: 1rem 2rem;
      cursor: pointer;
      transition: background-color 0.2s;
      color: #333;
      font-size: 1.2rem;
      font-weight: 500;
    }
  
    .sidebar-item:hover {
      background-color: #d8eef1;
    }
  
    .sidebar-item.active {
      background-color: #d8eef1;
    }
  
    .sidebar-item .icon {
      margin-right: 1rem;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  
    .sidebar-item.create .icon {
      font-size: 1.8rem;
      font-weight: 300;
    }
  
    .divider {
      height: 1px;
      background-color: #cce8eb;
      margin: 1rem 0;
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
    }
  </style>