<script lang="ts">
  import { onMount } from 'svelte';
  import CreateQuiz from './CreateQuiz.svelte';
  import QuizDetail from './QuizDetail.svelte';
  import EditQuiz from './EditQuiz.svelte';

  let userEmail = '';
  let isAdmin = false;

  // Tracks which section to display: 'home' | 'create' | 'my' | 'others' | 'quiz-detail'
  let currentSection: 'home' | 'create' | 'my' | 'others' | 'quiz-detail' | 'edit' = 'home';
  let editingQuizId: string | null = null;

  type Quiz = {
    _id: string;
    title: string;
    date_created: string;
    terms?: Array<{ term: string; description: string }>;
  };
  let myQuizzes: Quiz[] = [];

  type PublicQuiz = {
    _id: string;
    title: string;
    creator_username: string;
    date_created: string;
    terms?: Array<{ term: string; description: string }>;
  };
  let otherQuizzes: PublicQuiz[] = [];
  let selectedQuiz: Quiz | PublicQuiz | null = null;
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

    // Add mock data for demonstration
    myQuizzes = [
      {
        _id: '1',
        title: 'Quiz 1',
        date_created: new Date().toISOString(),
        terms: [
          {
            term: 'Term 1',
            description: 'Definition 1 - Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus et lacinia augue. Integer non mattis lacus. Curabitur a tortor a arcu tempor suscipit eu sit amet odio.'
          },
          {
            term: 'Term 2', 
            description: 'Definition 2 - Nam viverra nulla eget libero accumsan commodo ultricies a lacus. Suspendisse potenti. Phasellus at velit dapibus, viverra augue eget, dignissim tellus.'
          },
          {
            term: 'Term 3',
            description: 'Definition 3 - Integer egestas eu justo ac rhoncus.'
          },
          {
            term: 'Term 4',
            description: 'Definition 4 - Cras ut velit eu ante placerat semper. Etiam diam eros, fringilla eu diam a, porta aliquam orci. Aenean enim felis, rhoncus vel.'
          }
        ]
      },
      {
        _id: '2',
        title: 'Science Quiz',
        date_created: new Date().toISOString(),
        terms: [
          { term: 'Photosynthesis', description: 'The process by which plants convert sunlight into energy' },
          { term: 'Mitosis', description: 'Cell division that results in two identical daughter cells' }
        ]
      }
    ];

    otherQuizzes = [
      {
        _id: '3',
        title: 'History Quiz',
        creator_username: 'teacher@example.com',
        date_created: new Date().toISOString(),
        terms: [
          { term: 'Renaissance', description: 'A period of cultural rebirth in Europe' },
          { term: 'Industrial Revolution', description: 'The transition to manufacturing processes' }
        ]
      }
    ];
  });



  // Switch to home section
  function showHome() {
    currentSection = 'home';
    selectedQuiz = null;
    myQuizzes = [];
    otherQuizzes = [];
  }

  // Switch to create quiz form
  function openCreateQuiz() {
    currentSection = 'create';
    selectedQuiz = null;
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
          date_created: q.date_created,
          terms: q.terms || []
        }));
      } else {
        console.error('Error in get_user_quizzes:', data.message);
        // Keep mock data for demo
      }
    } catch (err) {
      console.error('Error fetching my quizzes:', err);
      // Keep mock data for demo
    } finally {
      currentSection = 'my';
      selectedQuiz = null;
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
            date_created: q.date_created,
            terms: q.terms || []
          }));
      } else {
        console.error('Error in get_public_quizzes:', data.message);
        // Keep mock data for demo
      }
    } catch (err) {
      console.error('Error fetching other quizzes:', err);
      // Keep mock data for demo
    } finally {
      currentSection = 'others';
      selectedQuiz = null;
    }
  }

  function openEditQuiz(quizId: string) {
  editingQuizId = quizId;
  currentSection = 'edit';
}

function handleEditClose() {
  editingQuizId = null;
  currentSection = 'home';
}

function handleQuizUpdated() {
  editingQuizId = null;
  loadMyQuizzes(); // Refresh the quiz list
}

  // Handle quiz card click
  function handleQuizClick(quiz: Quiz | PublicQuiz) {
    selectedQuiz = quiz;
    currentSection = 'quiz-detail';
  }

  // Handle close event from CreateQuiz component
  function handleCreateClose() {
    currentSection = 'home';
    selectedQuiz = null;
  }

  // Handle created event from CreateQuiz component
  // Reload the user's quizzes and switch to the 'my' section
  function handleQuizCreated() {
    loadMyQuizzes();
  }

  // Handle back from quiz detail
  function handleQuizDetailBack() {
    selectedQuiz = null;
    currentSection = 'home';
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
    <div class="sidebar-item create" onclick={openCreateQuiz}>
      <span class="icon">＋</span>
      <span class="text">Create</span>
    </div>

    <div class="divider"></div>

    <div class="sidebar-item" onclick={showHome}>
      <span class="icon">🏠</span>
      <span class="text">Home</span>
    </div>

    <div class="sidebar-item" onclick={loadMyQuizzes}>
      <span class="icon">📁</span>
      <span class="text">My quizzes</span>
    </div>

    <div class="sidebar-item" onclick={loadOtherQuizzes}>
      <span class="icon">👥</span>
      <span class="text">Study with others' quizzes</span>
    </div>
  </aside>

  <!-- Main content -->
  <main class="main-content">
    {#if currentSection === 'edit' && editingQuizId}
  <EditQuiz 
    quizId={editingQuizId}
    on:close={handleEditClose}
    on:updated={handleQuizUpdated}
  />
    {:else if currentSection === 'create'}
      <CreateQuiz
        on:close={handleCreateClose}
        on:created={handleQuizCreated}
      />
    {:else if currentSection === 'quiz-detail' && selectedQuiz}
      <QuizDetail 
        quiz={selectedQuiz} 
        on:back={handleQuizDetailBack}
      />
    {:else if currentSection === 'my'}
      <section class="quizzes-section">
        <h2 class="section-title">My recent quizzes</h2>
        <div class="quiz-section-wrapper">
          <button
            class="scroll-arrow left"
            onclick={() => scrollContainer('my-quizzes', 'left')}
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
                    <div class="quiz-actions">
                      <button class="edit-btn" onclick={() => openEditQuiz(quiz._id)}>
                        Edit
                      </button>
                      <button class="view-btn" onclick={() => handleQuizClick(quiz)}>
                        View
                      </button>
                    </div>
                  </div>
                  {/each}
              {/if}
            </div>
          </div>

          <button
            class="scroll-arrow right"
            onclick={() => scrollContainer('my-quizzes', 'right')}
          >
            &gt;
          </button>
        </div>
      </section>
    {:else if currentSection === 'others'}
      <!-- Others' public quizzes list -->
      <section class="quizzes-section">
        <h2 class="section-title">Study with others' quizzes</h2>
        <div class="quiz-section-wrapper">
          <button
            class="scroll-arrow left"
            onclick={() => scrollContainer('other-quizzes', 'left')}
          >
            &lt;
          </button>

          <div class="quiz-cards-container" id="other-quizzes">
            <div class="quiz-cards">
              {#if otherQuizzes.length === 0}
                <p>No public quizzes available.</p>
              {:else}
                {#each otherQuizzes as quiz (quiz._id)}
                  <div class="quiz-card" role="button" tabindex="0" onclick={() => handleQuizClick(quiz)} onkeydown={() => handleQuizClick(quiz)}>
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
            onclick={() => scrollContainer('other-quizzes', 'right')}
          >
            &gt;
          </button>
        </div>
      </section>
    
    {:else}
      <section>
        <h2>Welcome to Quizzle</h2>
        <p>Use the menu on the left to "Create," view "My quizzes," or "Study with others' quizzes."</p>
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
  
  .quiz-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
}

.edit-btn, .view-btn {
  flex: 1;
  padding: 0.625rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  position: relative;
  overflow: hidden;
}

.edit-btn {
  background: linear-gradient(135deg, #e8f4f6 0%, #d8eef1 100%);
  color: #2c5f66;
  border: 1px solid #c2e4e8;
}

.edit-btn:hover {
  background: linear-gradient(135deg, #d8eef1 0%, #c2e4e8 100%);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(44, 95, 102, 0.15);
  border-color: #a8d8dd;
}

.edit-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(44, 95, 102, 0.2);
}

.view-btn {
  background: linear-gradient(135deg, #e8f4f6 0%, #d8eef1 100%);
  color: #2c5f66;
  border: 1px solid #c2e4e8;
}

.view-btn:hover {
  background: linear-gradient(135deg, #d8eef1 0%, #c2e4e8 100%);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(44, 95, 102, 0.15);
  border-color: #a8d8dd;
}

.view-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(44, 95, 102, 0.4);
}

.edit-btn::before {
  font-size: 0.75rem;
}

.view-btn::before {
  font-size: 0.75rem;
}

.edit-btn.text-icon::before {
  font-family: Arial, sans-serif;
}

.view-btn.text-icon::before {
  content: "▶";
  font-family: Arial, sans-serif;
}

.edit-btn::after, .view-btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.3s, height 0.3s;
}

.edit-btn:active::after {
  width: 120px;
  height: 120px;
}

.view-btn:active::after {
  width: 120px;
  height: 120px;
  background: rgba(255, 255, 255, 0.2);
}

.quiz-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 1.5rem;
  min-width: 220px;
  cursor: default; 
  transition: all 0.3s ease;
  flex-shrink: 0;
  background: white;
  position: relative;
}

.quiz-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(44, 95, 102, 0.1);
  border-color: #c2e4e8;
}

@media (max-width: 768px) {
  .quiz-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .edit-btn, .view-btn {
    width: 100%;
  }
}
  
</style>
