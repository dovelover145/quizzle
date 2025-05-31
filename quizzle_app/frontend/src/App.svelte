<script lang="ts">
  import { onMount } from 'svelte';
  import Dashboard from './Dashboard.svelte';
  import Counter from './lib/Counter.svelte';

  let apiKey: string = '';
  let showDashboard = $state(false);
  let userEmail = null;
  let isAdmin = $state(false);

  onMount(async () => {
    /* try {
      const res = await fetch('/api/key');
      const data = await res.json();
      apiKey = data.apiKey;
    } catch (error) {
      console.error('Failed to fetch API key:', error);
    } */
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

  function handleCreateClick() {
    if (userEmail) {
      showDashboard = true;
    } else {
      window.location.href = 'http://localhost:8000/login';
    }
  }
</script>

<main>
  <header>
    <div class="header-left">
      <h1 class="logo">Quiz App</h1>
    </div>
    {#if userEmail}
        <div class="account-dropdown">
          <button class="account-btn">
            {userEmail} <span class="arrow">▼</span>
          </button>
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
