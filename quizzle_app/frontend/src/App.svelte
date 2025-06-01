<script lang="ts">
  import { onMount } from 'svelte';
  import Dashboard from './Dashboard.svelte';
  import CreateQuiz from './CreateQuiz.svelte';
  import Counter from './lib/Counter.svelte';

  let apiKey: string = '';
  let showDashboard = false;
  let userEmail: string | null = null;
  let userName: string | null = null;
  let isAdmin = false;
  let showDropdown = false;

  onMount(async () => {
    /* try {
      const res = await fetch('/api/key');
      const data = await res.json();
      apiKey = data.apiKey;
    } catch (error) {
      console.error('Failed to fetch API key:', error);
    } */
    try {
      const res = await fetch("http://localhost:8000/user_info", { credentials: "include" });
      if (res.ok) {
        const data = await res.json();
        userEmail = data.user.email;
        userName = data.user.name;
      }
    } catch (err) {
      console.error("Failed to fetch user", err);
    }
  }); 

  function handleCreateClick() {
    if (userEmail) {
      showDashboard = true;
    } else {
      window.location.href = 'http://localhost:8000/login';
    }
  }

  function toggleDropdown() {
    showDropdown = !showDropdown;
  }

  function closeDropdown() {
    showDropdown = false;
  }

  function logout() {
    window.location.href = 'http://localhost:8000/logout';
  }

  // Close dropdown when clicking outside
  function handleClickOutside(event: MouseEvent) {
    const target = event.target as Element;
    if (!target.closest('.account-dropdown')) {
      closeDropdown();
    }
  }
</script>

<svelte:window on:click={handleClickOutside} />

<main>
  <header>
    <div class="header-left">
      <h1 class="logo">Quiz App</h1>
    </div>
    {#if userEmail}
        <div class="account-dropdown">
          <button class="account-btn" on:click={toggleDropdown}>
            {userName} <span class="arrow" class:rotated={showDropdown}>▼</span>
          </button>
          {#if showDropdown}
            <div class="dropdown-menu">
              <div class="dropdown-item user-info">
                <span class="user-email">{userEmail}</span>
              </div>
              <div class="dropdown-divider"></div>
              <button class="dropdown-item logout-btn" on:click={logout}>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                  <polyline points="16 17 21 12 16 7"></polyline>
                  <line x1="21" y1="12" x2="9" y2="12"></line>
                </svg>
                Logout
              </button>
            </div>
          {/if}
        </div>
    {:else}
      <button class="login-btn" on:click={() => window.location.href = 'http://localhost:8000/login'}>Log in</button>
    {/if}
  </header>

  {#if showDashboard}
    <Dashboard />
  {:else}
    <section class="hero">
      <div class="hero-content">
        <h2 class="hero-title">
          Studying made <span class="highlight">easy</span> with Quiz App!
        </h2>
        <button
          class="cta-btn"
          on:click={handleCreateClick}
        >
          Create now
        </button>
      </div>
    </section>
  {/if}
</main>

<style>



</style>
