<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { TaskPlan } from '$lib/types';
  import type { Socket } from 'socket.io-client';

  let plan: TaskPlan | null = null;
  let socket: Socket | null = null; // Make socket available to the whole component

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

  // Clean up the socket connection when the user navigates away
  onDestroy(() => {
    socket?.disconnect();
  });

  // This function can now access the socket instance
  function sendHumanAction(stepId: string, action: string) {
    if (!socket) {
      console.error("Socket not connected.");
      return;
    }
    const payload = { step_id: stepId, action: action, approved: true, comments: "Looks good!" };
    socket.emit('human_action', payload);
    console.log('Sent human_action:', payload);
  }

  // A helper object to map step statuses to Tailwind CSS color classes for styling.
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
              <!-- Step Number Bubble -->
              <div class="flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-full mr-4 {step.status === 'completed' ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-700 font-semibold'}">
                {i + 1}
              </div>

              <!-- Step Details -->
              <div class="flex-grow border-b pb-4">
                <p class="font-semibold text-lg text-gray-800">{step.description}</p>
                <p class="text-sm font-medium capitalize {statusClasses[step.status]} px-2 py-1 rounded-md inline-block mt-1">
                  {step.status.replace(/_/g, ' ')}
                </p>

                <!-- Human-in-the-Loop Action Area -->
                {#if step.status === 'waiting_for_human'}
                  <div class="mt-4 border-t pt-4">
                    <p class="text-sm font-semibold text-gray-700 mb-2">Awaiting your input:</p>
                    <button
                      on:click={() => sendHumanAction(step.id, 'approve')}
                      class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-transform transform hover:scale-105"
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
        <!-- Loading State -->
        <div class="text-center py-12">
          <p class="text-xl text-gray-500 animate-pulse">Waiting for workflow from backend...</p>
        </div>
      {/if}
    </div>
  </div>
</main>