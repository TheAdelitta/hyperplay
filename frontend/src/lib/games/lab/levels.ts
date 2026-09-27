// src/lib/games/lab/levels.ts
//
// These are exactly what the model should return for the three sample PDFs.
// They are also compiled into the app as fallbacks, so every demo works with
// no network at all. Keyed by the subject the student picked on the upload
// screen, which is how the routing table finds them.
//
// Every stage below was verified by sweeping the full slider grid. If you edit
// a target, a range, or a lock, re-verify.

import type { LabLevel } from './types';

// ---------------------------------------------------------------------------
// CHEMISTRY  ·  High school, grade 11, Chemistry I
// Source: chemistry-gas-laws-grade11.pdf
// ---------------------------------------------------------------------------

export const chemistryGasLaws: LabLevel = {
	gameType: 'lab',
	visualMode: 'fill',

	concept: 'Ideal gas law, volume as a response to pressure and temperature',
	sourceSummary:
		'The chapter derives PV = nRT and rearranges it to solve for volume, noting that pressure and temperature push volume in opposite directions.',

	formula: 'V = nRT / P',
	expression: '(n * R * T) / P',

	controls: [
		{ key: 'P', label: 'Pressure', unit: 'kPa', min: 50, max: 300, step: 1, default: 100, decimals: 0 },
		{ key: 'T', label: 'Temperature', unit: 'K', min: 150, max: 600, step: 1, default: 300, decimals: 0 }
	],

	constants: { n: 1, R: 8.314 },

	output: { label: 'Volume', unit: 'L', decimals: 1, min: 0, max: 60 },

	stages: [
		{
			challenge: 'Hold the temperature at 300 K. Compress the gas to 18.0 L.',
			teaches: 'Pressure alone, with temperature held still.',
			target: { value: 18.0, tolerance: 0.5 },
			lock: { key: 'T', value: 300, note: 'Temperature is fixed for this challenge' },
			hints: [
				'Only pressure can move. Push it up and watch the piston.',
				'Volume and pressure are inversely proportional. More pressure, less volume.',
				'V = nRT / P. At 300 K you need a pressure near 139 kPa.'
			],
			debriefing:
				'Pressure and volume are inversely proportional. Raising the pressure squeezed the same number of particles into a smaller space. That is Boyle\u2019s law.'
		},
		{
			challenge: 'Now hold the pressure at 100 kPa. Expand the gas to 40.0 L.',
			teaches: 'Temperature alone, with pressure held still.',
			target: { value: 40.0, tolerance: 0.6 },
			lock: { key: 'P', value: 100, note: 'Pressure is fixed for this challenge' },
			hints: [
				'Only temperature can move this time. Which direction should it go?',
				'Hotter particles move faster and push the piston outward.',
				'Volume is directly proportional to absolute temperature. You need about 481 K.'
			],
			debriefing:
				'Volume and temperature are directly proportional. Heating the gas made its particles strike the walls harder, so it expanded. That is Charles\u2019s law, and it points the opposite way to pressure.'
		},
		{
			challenge: 'Both controls are unlocked. Set the gas to exactly 25.0 L.',
			teaches: 'The two effects competing in one equation.',
			target: { value: 25.0, tolerance: 0.5 },
			hints: [
				'There is more than one answer here. Find any of them.',
				'Raising both pressure and temperature together can leave the volume unchanged.',
				'Try 100 kPa at 300 K. Then try 200 kPa at 600 K and compare the two piston positions.'
			],
			debriefing:
				'You found one of many conditions that give 25.0 L. Because two variables appear in one equation, a whole family of pressure and temperature pairs satisfies it. That is why a gas has no fixed volume of its own.'
		}
	],

	readouts: [
		{ label: 'Temperature', expression: 'T - 273.15', unit: '\u00b0C', decimals: 0 },
		{ label: 'Moles of gas', expression: 'n', unit: 'mol', decimals: 2 },
		{ label: 'Particle energy', expression: 'T / 300', unit: '\u00d7 baseline', decimals: 2 }
	],

	completion:
		'You separated the two effects, then combined them. Pressure compresses, temperature expands, and the volume you observe is whichever wins. A gas has no volume of its own, only the volume its conditions allow.',

	difficulty: 'high',
	subject: 'Chemistry',
	courseLabel: 'Chemistry I \u00b7 Grade 11'
};

// ---------------------------------------------------------------------------
// BIOLOGY  ·  College, first year, General Biology I
// Source: biology-population-growth-college.pdf
// ---------------------------------------------------------------------------

export const biologyLogisticGrowth: LabLevel = {
	gameType: 'lab',
	visualMode: 'curve',

	concept: 'Logistic population growth, the roles of r and K',
	sourceSummary:
		'The chapter contrasts exponential and logistic growth and stresses that the intrinsic rate of increase sets the steepness while the carrying capacity sets the ceiling.',

	formula: 'N(t) = K / (1 + ((K \u2212 N\u2080) / N\u2080) \u00b7 e^(\u2212rt))',
	expression: 'K / (1 + ((K - N0) / N0) * exp(0 - r * 15))',

	controls: [
		{ key: 'r', label: 'Intrinsic growth rate', unit: 'per year', min: 0.05, max: 0.4, step: 0.01, default: 0.2, decimals: 2 },
		{ key: 'K', label: 'Carrying capacity', unit: 'deer', min: 100, max: 1000, step: 10, default: 500, decimals: 0 }
	],

	constants: { N0: 20 },

	output: { label: 'Population at year 15', unit: 'deer', decimals: 0, min: 0, max: 1000 },

	stages: [
		{
			challenge: 'The reserve holds 500 deer. Reach 400 of them by year 15.',
			teaches: 'The growth rate alone, with the ceiling held still.',
			target: { value: 400, tolerance: 14 },
			lock: { key: 'K', value: 500, note: 'Carrying capacity is fixed for this challenge' },
			hints: [
				'Only the growth rate can move. Watch how the curve bends.',
				'A higher rate does not raise the ceiling. It reaches the ceiling sooner.',
				'You need a rate near 0.30 per year.'
			],
			debriefing:
				'The growth rate controls the steepness of the climb, not where it stops. You reached 80 percent of the ceiling by year 15 without changing the ceiling at all.'
		},
		{
			challenge: 'Now the growth rate is stuck at 0.15. Reach 150 deer by year 15.',
			teaches: 'The carrying capacity alone, with the rate held still.',
			target: { value: 150, tolerance: 7 },
			lock: { key: 'r', value: 0.15, note: 'Growth rate is fixed for this challenge' },
			hints: [
				'Only the carrying capacity can move now.',
				'With a slow rate the population is still early on its curve, so raising the ceiling raises where it has got to.',
				'A capacity near 640 gets you there.'
			],
			debriefing:
				'A slow growing population is nowhere near its ceiling at year 15, so the ceiling still limits it. Notice you could not reach 400 this way at all. A low rate caps what is achievable in a fixed time.'
		},
		{
			challenge: 'Both controls are unlocked. Reach 350 deer by year 15, then find a second way to do it.',
			teaches: 'Two different populations passing through the same point.',
			target: { value: 350, tolerance: 12 },
			hints: [
				'Start with a fast rate and a low ceiling.',
				'Then try a slow rate and a high ceiling. Compare the two curve shapes.',
				'r = 0.32 with K = 400 works. So does r = 0.22 with K = 870.'
			],
			debriefing:
				'A fast growing population near its ceiling and a slow growing population far from a much higher ceiling both pass through 350 at year 15. The endpoint is the same. The curves are not. This is why field ecologists need both numbers rather than one.'
		}
	],

	series: {
		variable: 't',
		label: 'Years',
		unit: 'yr',
		min: 0,
		max: 30,
		steps: 120,
		expression: 'K / (1 + ((K - N0) / N0) * exp(0 - r * t))',
		markAt: 15
	},

	readouts: [
		{ label: 'Fastest growth at', expression: 'K / 2', unit: 'deer', decimals: 0 },
		{ label: 'Starting population', expression: 'N0', unit: 'deer', decimals: 0 },
		{ label: 'Percent of ceiling', expression: '100 * (K / (1 + ((K - N0) / N0) * exp(0 - r * 15))) / K', unit: '%', decimals: 0 }
	],

	completion:
		'You isolated each parameter, then saw them trade off. The rate bends the curve. The capacity sets the ceiling. A population is described by both, and knowing only its size at one moment tells you almost nothing about which it was.',

	difficulty: 'college',
	subject: 'Biology',
	courseLabel: 'General Biology I \u00b7 First year'
};

// ---------------------------------------------------------------------------
// MATH  ·  High school, grade 10, Algebra II
// Source: math-compound-interest-grade10.pdf
// ---------------------------------------------------------------------------

export const mathCompoundInterest: LabLevel = {
	gameType: 'lab',
	visualMode: 'meter',

	concept: 'Compound interest and exponential growth',
	sourceSummary:
		'The chapter develops A = P(1 + r)^t for annual compounding and shows that the rate sits in the base while time sits in the exponent.',

	formula: 'A = P(1 + r)^t',
	expression: 'P * (1 + r / SCALE) ^ t',

	controls: [
		{ key: 'r', label: 'Annual interest rate', unit: '%', min: 1, max: 15, step: 0.5, default: 5, decimals: 1 },
		{ key: 't', label: 'Years invested', unit: 'yr', min: 1, max: 40, step: 1, default: 10, decimals: 0 }
	],

	constants: { P: 1000, SCALE: 100 },

	output: { label: 'Final balance', unit: 'USD', decimals: 0, min: 0, max: 12000 },

	stages: [
		{
			challenge: 'The rate is fixed at 5 percent. Double your money to 2,000 dollars.',
			teaches: 'Time alone, with the rate held still.',
			target: { value: 2000, tolerance: 100 },
			lock: { key: 'r', value: 5, note: 'Interest rate is fixed for this challenge' },
			hints: [
				'Only the years slider can move. Drag it slowly and watch the early years.',
				'Notice how little the first few years add compared with the last few.',
				'The rule of 72 says 72 divided by 5 is about 14 years.'
			],
			debriefing:
				'It took about 14 years. The rate never changed, but each year the same percentage was applied to a larger balance, so the growth accelerated on its own.'
		},
		{
			challenge: 'Now the horizon is fixed at 20 years. Reach 2,900 dollars.',
			teaches: 'The rate alone, with time held still.',
			target: { value: 2900, tolerance: 80 },
			lock: { key: 't', value: 20, note: 'The investment period is fixed for this challenge' },
			hints: [
				'Only the rate can move now. Small changes do more than you expect.',
				'The rate sits inside the base, so it is applied twenty times over.',
				'You need about 5.5 percent.'
			],
			debriefing:
				'A rate change of half a percent moved the final balance by hundreds of dollars. That is because the rate is inside the base and compounds on itself every period.'
		},
		{
			challenge: 'Both controls are unlocked. Reach 5,000 dollars, then find a second way.',
			teaches: 'Rate and time trading off against each other.',
			target: { value: 5000, tolerance: 120 },
			hints: [
				'A higher rate needs fewer years. A longer horizon needs a lower rate.',
				'Find one answer, then deliberately halve the rate and see how many years it costs you.',
				'5 percent over 33 years works. So does 8 percent over 21 years.'
			],
			debriefing:
				'You found more than one route to 5,000 dollars. A higher return shortens the wait and a longer horizon lowers the return required. That trade off is the practical content of the whole formula.'
		}
	],

	readouts: [
		{ label: 'Interest earned', expression: 'P * (1 + r / SCALE) ^ t - P', unit: 'USD', decimals: 0 },
		{ label: 'Doubling time, rule of 72', expression: '72 / r', unit: 'yr', decimals: 1 },
		{ label: 'Growth multiple', expression: '(1 + r / SCALE) ^ t', unit: '\u00d7', decimals: 2 }
	],

	completion:
		'You isolated time, then the rate, then traded them against each other. Time sits in the exponent and rewards patience. The rate sits in the base and compounds on itself. Every saving decision is a choice between the two.',

	difficulty: 'high',
	subject: 'Mathematics',
	courseLabel: 'Algebra II \u00b7 Grade 10'
};

// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// PHYSICS  ·  High school, grade 11, Physics I
// No sample PDF. Matches the projectile challenge on the landing page.
// ---------------------------------------------------------------------------

export const physicsProjectileMotion: LabLevel = {
	gameType: 'lab',
	visualMode: 'trajectory',

	concept: 'Projectile range from launch angle and launch speed',
	sourceSummary:
		'A projectile launched from level ground travels a range set by the square of its launch speed and the sine of twice its launch angle.',

	formula: 'R = v\u00b2 sin(2\u03b8) / g',
	expression: 'v ^ 2 * sin(2 * theta * PI / 180) / g',

	// Trajectory mode reads the angle from the control measured in degrees.
	controls: [
		{ key: 'theta', label: 'Launch angle', unit: '\u00b0', min: 15, max: 75, step: 1, default: 45, decimals: 0 },
		{ key: 'v', label: 'Launch speed', unit: 'm/s', min: 5, max: 35, step: 0.5, default: 15, decimals: 1 }
	],

	constants: { g: 9.8 },

	output: { label: 'Range', unit: 'm', decimals: 1, min: 0, max: 130 },

	stages: [
		{
			challenge: 'The angle is fixed at 30\u00b0. Land the ball 50 meters away.',
			teaches: 'Launch speed alone, with the angle held still.',
			target: { value: 50, tolerance: 1.5 },
			lock: { key: 'theta', value: 30, note: 'Launch angle is fixed for this challenge' },
			hints: [
				'Only the speed can move. Fire once and see which way you missed.',
				'Range grows with the square of speed, so small speed changes matter more than they look.',
				'At 30\u00b0 you need a launch speed of about 24 m/s.'
			],
			debriefing:
				'Doubling the speed would have quadrupled the range. Speed enters the range equation squared, which is why the ball overshot so quickly once you pushed it.'
		},
		{
			challenge: 'Now the speed is fixed at 20 m/s. Land the ball 35 meters away.',
			teaches: 'Launch angle alone, with the speed held still.',
			target: { value: 35, tolerance: 0.8 },
			lock: { key: 'v', value: 20, note: 'Launch speed is fixed for this challenge' },
			hints: [
				'Only the angle can move this time. Try a low angle and a high one.',
				'Range peaks at 45\u00b0 and falls away evenly on either side.',
				'Both 30\u00b0 and 60\u00b0 land in the same spot. Try each.'
			],
			debriefing:
				'Two different angles reach the same range, one low and fast across, one high and slow. Angles that add up to 90\u00b0 always land together, because sin(2\u03b8) is symmetric around 45\u00b0.'
		},
		{
			challenge: 'Both controls are unlocked. Land the ball 80 meters away, then find a second way.',
			teaches: 'Angle and speed trading off against each other.',
			target: { value: 80, tolerance: 2 },
			hints: [
				'A launch closer to 45\u00b0 needs less speed to go the same distance.',
				'Find one answer, then move the angle 15\u00b0 away from 45\u00b0 and see how much speed you have to add.',
				'45\u00b0 at 28 m/s works. So does 30\u00b0 at 30 m/s.'
			],
			debriefing:
				'Many pairs of angle and speed land at 80 meters. The closer you launch to 45\u00b0, the less speed you need, because 45\u00b0 splits the speed most evenly between staying up and moving forward.'
		}
	],

	readouts: [
		{ label: 'Maximum height', expression: 'v ^ 2 * sin(theta * PI / 180) ^ 2 / (2 * g)', unit: 'm', decimals: 1 },
		{ label: 'Flight time', expression: '2 * v * sin(theta * PI / 180) / g', unit: 's', decimals: 2 },
		{ label: 'Gravity', expression: 'g', unit: 'm/s\u00b2', decimals: 1 }
	],

	completion:
		'You isolated speed, then angle, then traded them against each other. Speed counts twice because it is squared. Angle counts through sin(2\u03b8), which peaks at 45\u00b0 and pairs every low launch with a high one.',

	difficulty: 'high',
	subject: 'Physics',
	courseLabel: 'Physics I \u00b7 Grade 11'
};

// ---------------------------------------------------------------------------

export const fallbackLevels: Record<string, LabLevel> = {
	Physics: physicsProjectileMotion,
	Chemistry: chemistryGasLaws,
	Biology: biologyLogisticGrowth,
	Mathematics: mathCompoundInterest
};

/** The upload screen says "Math"; the levels and prompt say "Mathematics". */
const SUBJECT_ALIASES: Record<string, string> = {
	Math: 'Mathematics',
	Maths: 'Mathematics',
	'Computer science': 'Computer Science'
};

export function canonicalSubject(subject: string): string {
	return SUBJECT_ALIASES[subject] ?? subject;
}

export function fallbackFor(subject: string): LabLevel {
	return fallbackLevels[canonicalSubject(subject)] ?? chemistryGasLaws;
}
