<script lang="ts">
  import { onMount } from 'svelte';
  import svelteLogo from './assets/svelte.svg';
  import viteLogo from '/vite.svg';
  import Counter from './lib/Counter.svelte';

  let apiKey: string = '';
  let userEmail = null;
  let isAdmin = false;

  onMount(async () => {
    try {
      const res = await fetch('/api/key');
      const data = await res.json();
      apiKey = data.apiKey;
    } catch (error) {
      console.error('Failed to fetch API key:', error);
    }
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

<main>
  <header>
    <div class="header-left">
      <h1 class="logo">Quiz App</h1>
    </div>
    <button class="login-btn" on:click={() => window.location.href = '/login'}>Log in</button>
  </header>

  <section class="hero">
    <div class="hero-content">
      <h2 class="hero-title">
        Studying made <span class="highlight">easy</span> with Quiz App!
      </h2>
      <button class="cta-btn">Create now</button>
    </div>
  </section>
</main>

<style>
  
</style>
