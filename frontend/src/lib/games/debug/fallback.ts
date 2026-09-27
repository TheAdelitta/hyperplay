// src/lib/games/debug/fallback.ts
//
// Compiled into the app. Used when the model call fails, the keys are missing,
// or validation rejects the generated level. The demo never shows a broken state.

import type { DebugLevel } from './types';

export const debugFallback: DebugLevel = {
	gameType: 'debug',
	concept: 'Comparison operators and initialization edge cases',
	sourceSummary:
		'The chapter covers iterating over arrays and tracking a running maximum with a comparison inside a loop.',

	functionName: 'findLargest',

	brokenCode: `function findLargest(numbers) {
  let largest = 0;
  for (const number of numbers) {
    if (number < largest) {
      largest = number;
    }
  }
  return largest;
}`,

	referenceCode: `function findLargest(numbers) {
  let largest = numbers[0];
  for (const number of numbers) {
    if (number > largest) {
      largest = number;
    }
  }
  return largest;
}`,

	expectedBehavior: 'Return the largest number in the array.',
	mission: 'The system must return the largest number. Find and fix the fault.',

	tests: [
		{
			name: 'Mixed positive numbers',
			args: [[3, 9, 2, 7]],
			expected: 9,
			failNote: 'The comparison inside the loop is pointing the wrong way.'
		},
		{
			name: 'Already in ascending order',
			args: [[1, 2, 3, 4, 5]],
			expected: 5,
			failNote: 'The loop is not keeping the larger value.'
		},
		{
			name: 'All negative numbers',
			args: [[-4, -1, -9]],
			expected: -1,
			failNote:
				'Starting from zero means every negative number loses the comparison. What should the starting value be?'
		},
		{
			name: 'Single element',
			args: [[42]],
			expected: 42,
			failNote: 'With one element the answer is that element.'
		}
	],

	hints: [
		'Read the condition inside the loop out loud. Does it describe what you want to keep?',
		'Fix the comparison first, then run the tests again and read which one still fails.',
		'A starting value of zero assumes the answer is positive. Start from the first element instead.'
	],

	debriefing:
		'You corrected two separate faults. The comparison decided which value to keep, and the initial value quietly assumed every number would be positive. The second fault only appears on negative input, which is exactly why edge case tests exist.',

	timeLimit: 300,
	difficulty: 'college'
};
