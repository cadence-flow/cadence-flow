<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { TaskPlan } from '$lib/types';
  import type { Socket } from 'socket.io-client';

  let plan: TaskPlan | null = null;
  let socket: Socket | null = null;

  onMount(async () => {
    const { io } = await import('socket.io-client');
    socket = io('http://127.0.0.1:8501');

    socket.on('connect', () => console.log('Successfully connected!'));
    socket.on('plan_update', (data: TaskPlan) => {
      console.log('Received plan_update:', data);
      plan = data;
    });
    socket.on('disconnect', () => console.log('Disconnected.'));
  });

  onDestroy(() => {
    socket?.disconnect();
  });

  function sendHumanAction(stepId: string, action: string) {
    if (!socket) {
      console.error("Socket not connected.");
      return;
    }
    const payload = { step_id: stepId, action: action, approved: true, comments: "Looks good!" };
    socket.emit('human_action', payload);
    console.log('Sent human_action:', payload);
  }

  const statusClasses: Record<string, string> = {
    pending: 'text-gray-500 bg-gray-100',
    running: 'text-blue-600 bg-blue-100 animate-pulse',
    waiting_for_human: 'text-yellow-600 bg-yellow-100 font-bold',
    completed: 'text-green-600 bg-green-100',
    failed: 'text-red-600 bg-red-100'
  };
</script>

<main class="bg-gray-100 min-h-screen font-sans p-4 sm:p-8">
  <div class="max-w-3xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden">
    <div class="p-6 sm:p-8">
      {#if plan}
        <h1 class="text-3xl font-bold text-gray-900 mb-2">{plan.title}</h1>
        <p class="text-sm text-gray-500 mb-8">Plan ID: {plan.plan_id}</p>

        <ol class="space-y-6">
          {#each plan.steps as step, i}
            <li class="flex items-start">
              <div class="flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full mr-4 {step.status === 'completed' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700 font-semibold'}">
                {i + 1}
              </div>
              <div class="flex-grow border-b pb-4">
                <p class="font-semibold text-lg text-gray-800">{step.description}</p>
                <p class="text-sm font-medium capitalize {statusClasses[step.status]} px-2 py-1 rounded-md inline-block mt-1">
                  {step.status.replace(/_/g, ' ')}
                </p>

                <!-- --- THIS IS THE BLOCK TO DISPLAY THE ERROR --- -->
                {#if step.status === 'failed' && step.error}
                  <div class="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                    <p class="font-semibold text-red-800 mb-2">Error Details:</p>
                    <pre class="text-xs text-red-700 overflow-x-auto bg-white p-2 rounded"><code>{step.error}</code></pre>
                  </div>
                {/if}
                <!-- --- END OF ERROR BLOCK --- -->

                {#if step.status === 'waiting_for_human'}
                  <div class="mt-4 border-t pt-4">
                    <p class="text-sm font-semibold text-gray-700 mb-2">Awaiting your input:</p>
                    <button
                      on:click={() => sendHumanAction(step.id, 'approve')}
                      class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg"
                    >
                      Approve & Continue
                    </button>
                  </div>
                {/if}
              </div>
            </li>
          {/each}
        </ol>
      {:else}
        <div class="text-center py-12">
          <p class="text-xl text-gray-500 animate-pulse">Waiting for workflow from backend...</p>
        </div>
      {/if}
    </div>
  </div>
</main>