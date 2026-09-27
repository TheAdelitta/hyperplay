// src/lib/games/lab/fewshot.ts
//
// You cannot fine-tune an Azure model during a hackathon. You do not need to.
// Showing the model two complete, verified examples inside the prompt makes its
// output on unseen chapters far more consistent than describing the schema
// alone. This is the cheapest accuracy win available.
//
// Both examples below were generated directly from the verified levels in
// levels.ts, so they cannot drift away from what the code actually plays.
// Every stage in both was confirmed solvable by sweeping the slider grid.

export const FEWSHOT_EXAMPLES = `
Here are two complete, correct outputs. Match this level of specificity, and
copy the stage ladder exactly: lock one control, lock the other, then unlock both.

EXAMPLE 1
Passage: a chapter deriving PV = nRT and rearranging it to solve for volume,
noting that pressure and temperature push volume in opposite directions.
Subject: Chemistry. Level: high.

{
  "gameType": "lab",
  "visualMode": "fill",
  "concept": "Ideal gas law, volume as a response to pressure and temperature",
  "sourceSummary": "The chapter derives PV = nRT and rearranges it to solve for volume, noting that pressure and temperature push volume in opposite directions.",
  "formula": "V = nRT / P",
  "expression": "(n * R * T) / P",
  "controls": [
    {
      "key": "P",
      "label": "Pressure",
      "unit": "kPa",
      "min": 50,
      "max": 300,
      "step": 1,
      "default": 100,
      "decimals": 0
    },
    {
      "key": "T",
      "label": "Temperature",
      "unit": "K",
      "min": 150,
      "max": 600,
      "step": 1,
      "default": 300,
      "decimals": 0
    }
  ],
  "constants": {
    "n": 1,
    "R": 8.314
  },
  "output": {
    "label": "Volume",
    "unit": "L",
    "decimals": 1,
    "min": 0,
    "max": 60
  },
  "stages": [
    {
      "challenge": "Hold the temperature at 300 K. Compress the gas to 18.0 L.",
      "teaches": "Pressure alone, with temperature held still.",
      "target": {
        "value": 18,
        "tolerance": 0.5
      },
      "lock": {
        "key": "T",
        "value": 300,
        "note": "Temperature is fixed for this challenge"
      },
      "hints": [
        "Only pressure can move. Push it up and watch the piston.",
        "Volume and pressure are inversely proportional. More pressure, less volume.",
        "V = nRT / P. At 300 K you need a pressure near 139 kPa."
      ],
      "debriefing": "Pressure and volume are inversely proportional. Raising the pressure squeezed the same number of particles into a smaller space. That is Boyle’s law."
    },
    {
      "challenge": "Now hold the pressure at 100 kPa. Expand the gas to 40.0 L.",
      "teaches": "Temperature alone, with pressure held still.",
      "target": {
        "value": 40,
        "tolerance": 0.6
      },
      "lock": {
        "key": "P",
        "value": 100,
        "note": "Pressure is fixed for this challenge"
      },
      "hints": [
        "Only temperature can move this time. Which direction should it go?",
        "Hotter particles move faster and push the piston outward.",
        "Volume is directly proportional to absolute temperature. You need about 481 K."
      ],
      "debriefing": "Volume and temperature are directly proportional. Heating the gas made its particles strike the walls harder, so it expanded. That is Charles’s law, and it points the opposite way to pressure."
    },
    {
      "challenge": "Both controls are unlocked. Set the gas to exactly 25.0 L.",
      "teaches": "The two effects competing in one equation.",
      "target": {
        "value": 25,
        "tolerance": 0.5
      },
      "hints": [
        "There is more than one answer here. Find any of them.",
        "Raising both pressure and temperature together can leave the volume unchanged.",
        "Try 100 kPa at 300 K. Then try 200 kPa at 600 K and compare the two piston positions."
      ],
      "debriefing": "You found one of many conditions that give 25.0 L. Because two variables appear in one equation, a whole family of pressure and temperature pairs satisfies it. That is why a gas has no fixed volume of its own."
    }
  ],
  "readouts": [
    {
      "label": "Temperature",
      "expression": "T - 273.15",
      "unit": "°C",
      "decimals": 0
    },
    {
      "label": "Moles of gas",
      "expression": "n",
      "unit": "mol",
      "decimals": 2
    },
    {
      "label": "Particle energy",
      "expression": "T / 300",
      "unit": "× baseline",
      "decimals": 2
    }
  ],
  "completion": "You separated the two effects, then combined them. Pressure compresses, temperature expands, and the volume you observe is whichever wins. A gas has no volume of its own, only the volume its conditions allow.",
  "difficulty": "high",
  "subject": "Chemistry",
  "courseLabel": "Chemistry I · Grade 11"
}

EXAMPLE 2
Passage: a chapter contrasting exponential and logistic growth, stressing that
the intrinsic rate of increase sets the steepness while the carrying capacity
sets the ceiling.
Subject: Biology. Level: college.

{
  "gameType": "lab",
  "visualMode": "curve",
  "concept": "Logistic population growth, the roles of r and K",
  "sourceSummary": "The chapter contrasts exponential and logistic growth and stresses that the intrinsic rate of increase sets the steepness while the carrying capacity sets the ceiling.",
  "formula": "N(t) = K / (1 + ((K − N₀) / N₀) · e^(−rt))",
  "expression": "K / (1 + ((K - N0) / N0) * exp(0 - r * 15))",
  "controls": [
    {
      "key": "r",
      "label": "Intrinsic growth rate",
      "unit": "per year",
      "min": 0.05,
      "max": 0.4,
      "step": 0.01,
      "default": 0.2,
      "decimals": 2
    },
    {
      "key": "K",
      "label": "Carrying capacity",
      "unit": "deer",
      "min": 100,
      "max": 1000,
      "step": 10,
      "default": 500,
      "decimals": 0
    }
  ],
  "constants": {
    "N0": 20
  },
  "output": {
    "label": "Population at year 15",
    "unit": "deer",
    "decimals": 0,
    "min": 0,
    "max": 1000
  },
  "stages": [
    {
      "challenge": "The reserve holds 500 deer. Reach 400 of them by year 15.",
      "teaches": "The growth rate alone, with the ceiling held still.",
      "target": {
        "value": 400,
        "tolerance": 14
      },
      "lock": {
        "key": "K",
        "value": 500,
        "note": "Carrying capacity is fixed for this challenge"
      },
      "hints": [
        "Only the growth rate can move. Watch how the curve bends.",
        "A higher rate does not raise the ceiling. It reaches the ceiling sooner.",
        "You need a rate near 0.30 per year."
      ],
      "debriefing": "The growth rate controls the steepness of the climb, not where it stops. You reached 80 percent of the ceiling by year 15 without changing the ceiling at all."
    },
    {
      "challenge": "Now the growth rate is stuck at 0.15. Reach 150 deer by year 15.",
      "teaches": "The carrying capacity alone, with the rate held still.",
      "target": {
        "value": 150,
        "tolerance": 7
      },
      "lock": {
        "key": "r",
        "value": 0.15,
        "note": "Growth rate is fixed for this challenge"
      },
      "hints": [
        "Only the carrying capacity can move now.",
        "With a slow rate the population is still early on its curve, so raising the ceiling raises where it has got to.",
        "A capacity near 640 gets you there."
      ],
      "debriefing": "A slow growing population is nowhere near its ceiling at year 15, so the ceiling still limits it. Notice you could not reach 400 this way at all. A low rate caps what is achievable in a fixed time."
    },
    {
      "challenge": "Both controls are unlocked. Reach 350 deer by year 15, then find a second way to do it.",
      "teaches": "Two different populations passing through the same point.",
      "target": {
        "value": 350,
        "tolerance": 12
      },
      "hints": [
        "Start with a fast rate and a low ceiling.",
        "Then try a slow rate and a high ceiling. Compare the two curve shapes.",
        "r = 0.32 with K = 400 works. So does r = 0.22 with K = 870."
      ],
      "debriefing": "A fast growing population near its ceiling and a slow growing population far from a much higher ceiling both pass through 350 at year 15. The endpoint is the same. The curves are not. This is why field ecologists need both numbers rather than one."
    }
  ],
  "series": {
    "variable": "t",
    "label": "Years",
    "unit": "yr",
    "min": 0,
    "max": 30,
    "steps": 120,
    "expression": "K / (1 + ((K - N0) / N0) * exp(0 - r * t))",
    "markAt": 15
  },
  "readouts": [
    {
      "label": "Fastest growth at",
      "expression": "K / 2",
      "unit": "deer",
      "decimals": 0
    },
    {
      "label": "Starting population",
      "expression": "N0",
      "unit": "deer",
      "decimals": 0
    },
    {
      "label": "Percent of ceiling",
      "expression": "100 * (K / (1 + ((K - N0) / N0) * exp(0 - r * 15))) / K",
      "unit": "%",
      "decimals": 0
    }
  ],
  "completion": "You isolated each parameter, then saw them trade off. The rate bends the curve. The capacity sets the ceiling. A population is described by both, and knowing only its size at one moment tells you almost nothing about which it was.",
  "difficulty": "college",
  "subject": "Biology",
  "courseLabel": "General Biology I · First year"
}

Note four things about these examples.

First, the stage ladder. Stage 1 freezes one control so a single relationship is
visible alone. Stage 2 freezes the other. Stage 3 unlocks both and picks a target
that several different pairs can reach. That ordering is what teaches.

Second, the locked stages have narrow answers and the unlocked stage has many.
That is correct. With one slider fixed, the student is solving for one value.

Third, example 2 uses "markAt". The logistic curve saturates well before year 30,
so scoring at year 30 would make the carrying capacity the only slider that
matters. Scoring at year 15 keeps both meaningful. Apply the same reasoning
whenever an output flattens before the end of its range.

Fourth, every specific value named in a third hint actually wins. Check yours.
`;

/**
 * If the passage has no two-variable quantitative relationship, the model
 * should say so rather than inventing one. Appended to the system prompt and
 * handled in the backend.
 */
export const UNFITTABLE_CLAUSE = `
If the passage contains no quantitative relationship between two adjustable
quantities, for example a narrative history chapter or a descriptive chapter
on anatomy, do not invent one. Return exactly this instead:

{ "gameType": "unfittable", "reason": "<one sentence on what the chapter covers>", "suggestion": "<one sentence naming the kind of chapter that would work>" }
`;
