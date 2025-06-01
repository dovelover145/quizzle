<!-- src/Dashboard.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import CreateQuiz from './CreateQuiz.svelte';

  let userEmail = '';
  let isAdmin = false;

  // Tracks which section to display: 'home' | 'create' | 'my' | 'others'
  let currentSection: 'home' | 'create' | 'my' | 'others' = 'home';

  // List of quizzes created by the logged-in user
  type Quiz = {
    _id: string;
    title: string;
    date_created: string;
  };
  let myQuizzes: Quiz[] = [];

  // List of public quizzes created by other users
  type PublicQuiz = {
    _id: string;
    title: string;
    creator_username: string;
    date_created: string;
  };
  let otherQuizzes: PublicQuiz[] = [];

  // Fetch user information on mount
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
        console.error('Failed to fetch user_info:', data.message);
        userEmail = '';
      }
    } catch (err) {
      console.error('Error fetching user_info:', err);
      userEmail = '';
    }
  });

  // Switch to home section
  function showHome() {
    currentSection = 'home';
    myQuizzes = [];
    otherQuizzes = [];
  }

  // Switch to create quiz form
  function openCreateQuiz() {
    currentSection = 'create';
  }

  // Fetch and display the logged-in user's quizzes
  async function loadMyQuizzes() {
    if (!userEmail) {
      alert('No login information found. Please log in again.');
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/get_user_quizzes', {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ creator_username: userEmail })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        myQuizzes = [
          ...data.public_quizzes,
          ...data.private_quizzes
        ].map((q: any) => ({
          _id: q._id,
          title: q.title,
          date_created: q.date_created
        }));
      } else {
        console.error('Error in get_user_quizzes:', data.message);
        myQuizzes = [];
      }
    } catch (err) {
      console.error('Error fetching my quizzes:', err);
      myQuizzes = [];
    } finally {
      currentSection = 'my';
    }
  }

  // Fetch and display public quizzes created by other users
  async function loadOtherQuizzes() {
    try {
      const res = await fetch('http://localhost:8000/get_public_quizzes', {
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      });
      const data = await res.json();
      if (res.ok && data.success) {
        otherQuizzes = data.public_quizzes
          .filter((q: any) => q.creator_username !== userEmail)
          .map((q: any) => ({
            _id: q._id,
            title: q.title,
            creator_username: q.creator_username,
            date_created: q.date_created
          }));
      } else {
        console.error('Error in get_public_quizzes:', data.message);
        otherQuizzes = [];
      }
    } catch (err) {
      console.error('Error fetching other quizzes:', err);
      otherQuizzes = [];
    } finally {
      currentSection = 'others';
    }
  }

  // Handle close event from CreateQuiz component
  function handleCreateClose() {
    currentSection = 'home';
  }

  // Handle created event from CreateQuiz component
  // Reload the user's quizzes and switch to the 'my' section
  function handleQuizCreated() {
    loadMyQuizzes();
  }

  // Helper function to scroll quiz lists horizontally
  function scrollContainer(containerId: string, direction: 'left' | 'right') {
    const container = document.getElementById(containerId);
    if (!container) return;
    const scrollAmount = 250;
    const currentScroll = container.scrollLeft;
    const targetScroll =
      direction === 'left'
        ? currentScroll - scrollAmount
        : currentScroll + scrollAmount;

    container.scrollTo({
      left: targetScroll,
      behavior: 'smooth'
    });
  }
</script>

<div class="dashboard-container">
  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-item create" on:click={openCreateQuiz}>
      <span class="icon">＋</span>
      <span class="text">Create</span>
    </div>

    <div class="divider"></div>

    <div class="sidebar-item" on:click={showHome}>
      <span class="icon">
        <!-- Home icon SVG -->
      </span>
      <span class="text">Home</span>
    </div>

    <div class="sidebar-item" on:click={loadMyQuizzes}>
      <span class="icon">
        <!-- My quizzes icon SVG -->
      </span>
      <span class="text">My quizzes</span>
    </div>

    <div class="sidebar-item" on:click={loadOtherQuizzes}>
      <span class="icon">
        <!-- Others' quizzes icon SVG -->
      </span>
      <span class="text">Study with others’ quizzes</span>
    </div>
  </aside>

  <!-- Main content -->
  <main class="main-content">
    {#if currentSection === 'create'}
      <!-- CreateQuiz component -->
      <CreateQuiz
        on:close={handleCreateClose}
        on:created={handleQuizCreated}
      />
    {:else if currentSection === 'my'}
      <!-- My quizzes list -->
      <section class="quizzes-section">
        <h2 class="section-title">My recent quizzes</h2>
        <div class="quiz-section-wrapper">
          <button
            class="scroll-arrow left"
            on:click={() => scrollContainer('my-quizzes', 'left')}
          >
            &lt;
          </button>

          <div class="quiz-cards-container" id="my-quizzes">
            <div class="quiz-cards">
              {#if myQuizzes.length === 0}
                <p>No quizzes created yet.</p>
              {:else}
                {#each myQuizzes as quiz (quiz._id)}
                  <div class="quiz-card">
                    <h3 class="quiz-title">{quiz.title}</h3>
                    <small>{new Date(quiz.date_created).toLocaleString()}</small>
                  </div>
                {/each}
              {/if}
            </div>
          </div>

          <button
            class="scroll-arrow right"
            on:click={() => scrollContainer('my-quizzes', 'right')}
          >
            &gt;
          </button>
        </div>
      </section>
    {:else if currentSection === 'others'}
      <!-- Others' public quizzes list -->
      <section class="quizzes-section">
        <h2 class="section-title">Study with others’ quizzes</h2>
        <div class="quiz-section-wrapper">
          <button
            class="scroll-arrow left"
            on:click={() => scrollContainer('other-quizzes', 'left')}
          >
            &lt;
          </button>

          <div class="quiz-cards-container" id="other-quizzes">
            <div class="quiz-cards">
              {#if otherQuizzes.length === 0}
                <p>No public quizzes available.</p>
              {:else}
                {#each otherQuizzes as quiz (quiz._id)}
                  <div class="quiz-card">
                    <h3 class="quiz-title">{quiz.title}</h3>
                    <p class="quiz-author">by {quiz.creator_username}</p>
                    <small>{new Date(quiz.date_created).toLocaleString()}</small>
                  </div>
                {/each}
              {/if}
            </div>
          </div>

          <button
            class="scroll-arrow right"
            on:click={() => scrollContainer('other-quizzes', 'right')}
          >
            &gt;
          </button>
        </div>
      </section>
    {:else}
      <!-- Home section -->
      <section>
        <h2>Welcome to Quiz App</h2>
        <p>Use the menu on the left to “Create,” view “My quizzes,” or “Study with others’ quizzes.”</p>
      </section>
    {/if}
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

  .sidebar-item .icon {
    margin-right: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
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
    font-size: 1.25rem;
    line-height: 1;
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
