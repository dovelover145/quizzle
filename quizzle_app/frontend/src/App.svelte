<script lang="ts">
  import { onMount } from 'svelte';
  import svelteLogo from './assets/svelte.svg';
  import viteLogo from '/vite.svg';
  import Counter from './lib/Counter.svelte';

  let apiKey: string = '';

  onMount(async () => {
    try {
      const res = await fetch('/api/key');
      const data = await res.json();
      apiKey = data.apiKey;
    } catch (error) {
      console.error('Failed to fetch API key:', error);
    }
  }); 
</script>

<main>
  <header>
    <div class="header-left">
      <h1 class="logo">Quiz App</h1>
    </div>
    <button class="login-btn">Log in</button>
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
