<script lang="ts">
    import { onMount } from 'svelte';
    
    let userEmail = $state('');
    let isAdmin = $state(false);
    
    let myQuizzes = $state([
      { id: 1, title: 'Quiz 1' },
      { id: 2, title: 'Quiz 2' }
    ]);
    
    let otherQuizzes = $state([
      { id: 1, title: 'Quiz 1', author: 'User' },
      { id: 2, title: 'Quiz 2', author: 'User' },
      { id: 3, title: 'Quiz 3', author: 'User' },
      { id: 4, title: 'Quiz 4', author: 'User' },
      { id: 5, title: 'Quiz 5', author: 'User' },
      { id: 6, title: 'Quiz 6', author: 'User' }
    ]);
    
    function scrollContainer(containerId: string, direction: 'left' | 'right') {
      const container = document.getElementById(containerId);
      if (container) {
        const scrollAmount = 250; 
        const currentScroll = container.scrollLeft;
        const targetScroll = direction === 'left' 
          ? currentScroll - scrollAmount 
          : currentScroll + scrollAmount;
        
        container.scrollTo({
          left: targetScroll,
          behavior: 'smooth'
        });
      }
    }
    
    onMount(async () => {
      try {
        const res = await fetch("/me", { credentials: "include" });
        if (res.ok) {
          const data = await res.json();
          userEmail = data.email;
        
        }
      } catch (err) {
        console.error("Failed to fetch user", err);
      }
    });
  </script>
  
  <div class="dashboard-container">
    <aside class="sidebar">
      <div class="sidebar-item create">
        <span class="icon">+</span>
        <span class="text">Create</span>
      </div>
      <div class="divider"></div>
      <div class="sidebar-item active">
        <span class="icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
        </span>
        <span class="text">Home</span>
      </div>
      <div class="sidebar-item">
        <span class="icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
          </span>
        <span class="text">My quizzes</span>
      </div>
    </aside>

    <main class="main-content">
      <section class="quizzes-section">
        <h2 class="section-title">My recent quizzes</h2>
        <div class="quiz-section-wrapper">
          <button class="scroll-arrow left" on:click={() => scrollContainer('my-quizzes', 'left')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
          </button> <!--https://www.w3.org/Graphics/SVG/WG/wiki/SVG_in_HTML-->
          <div class="quiz-cards-container" id="my-quizzes">
            <div class="quiz-cards">
              {#each myQuizzes as quiz}
                <div class="quiz-card">
                  <h3 class="quiz-title">{quiz.title}</h3>
                </div>
              {/each}
            </div>
          </div>
          <button class="scroll-arrow right" on:click={() => scrollContainer('my-quizzes', 'right')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
          </button>
        </div>
      </section>
  

      <section class="quizzes-section">
        <h2 class="section-title">Study with others' quizzes</h2>
        <div class="quiz-section-wrapper">
          <button class="scroll-arrow left" on:click={() => scrollContainer('other-quizzes', 'left')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
          </button>
          <div class="quiz-cards-container" id="other-quizzes">
            <div class="quiz-cards">
              {#each otherQuizzes as quiz}
                <div class="quiz-card">
                  <h3 class="quiz-title">{quiz.title}</h3>
                  <p class="quiz-author">by {quiz.author}</p>
                </div>
              {/each}
            </div>
          </div>
          <button class="scroll-arrow right" on:click={() => scrollContainer('other-quizzes', 'right')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
          </button>
        </div>
      </section>
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
    }
  
    .section-title {
      font-size: 1.8rem;
      font-weight: 600;
      color: #333;
      margin-bottom: 1.5rem;
    }
  
    .quiz-section-wrapper {
      position: relative;
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .scroll-arrow {
      background: white;
      border: 1px solid #e0e0e0;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s;
      color: #666;
      flex-shrink: 0;
      z-index: 10;
    }

    .scroll-arrow:hover {
      background: #f8f9fa;
      border-color: #d0d0d0;
      color: #333;
      transform: scale(1.05);
    }

    .scroll-arrow:active {
      transform: scale(0.95);
    }

    .quiz-cards-container {
      overflow-x: hidden; 
      flex: 1;
      position: relative;
    }

  
    .quiz-cards {
      display: flex;
      gap: 1.5rem;
      min-width: max-content;
    }
  
    .quiz-card {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 1.5rem;
      min-width: 200px;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
      flex-shrink: 0;
    }
  
    .quiz-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
  
    .quiz-title {
      font-size: 1.2rem;
      font-weight: 500;
      color: #333;
      margin: 0;
    }
  
    .quiz-author {
      font-size: 0.9rem;
      color: #666;
      margin: 0.5rem 0 0;
    }
  
    .quizzes-section {
      margin-bottom: 3rem;
    }
  </style>