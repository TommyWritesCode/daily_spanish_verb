const STORAGE_KEY = 'pastTenseTrainer_v1';

const DEFAULT_STATS = {
  conceptAccuracy: {
    INTERRUPTION: null,
    HABIT: null,
    REPEATED_PAST: null,
    DESCRIPTION: null,
    STATE: null,
    AGE: null,
    WEATHER: null,
    TIME: null,
    EVENT_SEQUENCE: null,
    COMPLETED_ACTION: null,
    COUNTED_REPETITION: null,
    MEANING_CHANGE: null,
    ONGOING_BACKGROUND: null,
  },
  tenseAccuracy: {
    PRETERITE: null,
    IMPERFECT: null,
  },
  verbFamilyAccuracy: {
    AR_PRET: null,
    ERIR_PRET: null,
    AR_IMP: null,
    ERIR_IMP: null,
  },
  streak: 0,
  totalReps: 0,
  recentResults: [], // last 20 results: {correct: bool}
  lastSeen: {},      // id -> ISO timestamp
  weaknessQueue: [], // ids to prioritize
  sessionErrors: {}, // conceptTag -> count this session
};

export function loadStats() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...DEFAULT_STATS };
    const parsed = JSON.parse(raw);
    // Merge with defaults so new keys appear
    return {
      ...DEFAULT_STATS,
      ...parsed,
      conceptAccuracy: { ...DEFAULT_STATS.conceptAccuracy, ...parsed.conceptAccuracy },
      tenseAccuracy: { ...DEFAULT_STATS.tenseAccuracy, ...parsed.tenseAccuracy },
      verbFamilyAccuracy: { ...DEFAULT_STATS.verbFamilyAccuracy, ...parsed.verbFamilyAccuracy },
    };
  } catch {
    return { ...DEFAULT_STATS };
  }
}

export function saveStats(stats) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(stats));
  } catch {
    // storage full or blocked
  }
}

export function clearStats() {
  localStorage.removeItem(STORAGE_KEY);
}

function updateAccuracy(current, isCorrect) {
  // Exponential moving average: weight recent results more
  if (current === null) return isCorrect ? 1.0 : 0.0;
  return current * 0.85 + (isCorrect ? 1 : 0) * 0.15;
}

function getVerbFamily(verb, tense) {
  const arVerbs = ['hablar', 'estudiar', 'trabajar', 'caminar', 'cocinar', 'cantar',
    'jugar', 'buscar', 'mirar', 'esperar', 'levantarse', 'viajar', 'ducharse',
    'tocar', 'manejar', 'preparar', 'llamar', 'levantarse', 'escuchar', 'salir',
    'llegar', 'comprar', 'empezar', 'terminar', 'caminar', 'beber', 'estar'];
  // default: check ending
  const isAR = verb.endsWith('ar') || arVerbs.includes(verb);
  if (tense === 'PRETERITE') return isAR ? 'AR_PRET' : 'ERIR_PRET';
  return isAR ? 'AR_IMP' : 'ERIR_IMP';
}

export function recordResult(stats, exercise, classificationCorrect, conjugationCorrect) {
  const overallCorrect = classificationCorrect && conjugationCorrect;
  const newStats = { ...stats };

  // Update streak
  if (overallCorrect) {
    newStats.streak = (stats.streak || 0) + 1;
  } else {
    newStats.streak = 0;
  }

  newStats.totalReps = (stats.totalReps || 0) + 1;

  // Recent results (last 20)
  newStats.recentResults = [
    { correct: overallCorrect },
    ...(stats.recentResults || []),
  ].slice(0, 20);

  // Update concept accuracy
  newStats.conceptAccuracy = { ...stats.conceptAccuracy };
  for (const tag of exercise.conceptTags) {
    if (newStats.conceptAccuracy[tag] !== undefined) {
      newStats.conceptAccuracy[tag] = updateAccuracy(newStats.conceptAccuracy[tag], overallCorrect);
    }
  }

  // Update tense accuracy
  newStats.tenseAccuracy = { ...stats.tenseAccuracy };
  newStats.tenseAccuracy[exercise.expectedTense] = updateAccuracy(
    stats.tenseAccuracy[exercise.expectedTense],
    classificationCorrect
  );

  // Update verb family accuracy (conjugation)
  newStats.verbFamilyAccuracy = { ...stats.verbFamilyAccuracy };
  const family = getVerbFamily(exercise.verb, exercise.expectedTense);
  newStats.verbFamilyAccuracy[family] = updateAccuracy(
    stats.verbFamilyAccuracy[family],
    conjugationCorrect
  );

  // Update lastSeen
  newStats.lastSeen = { ...stats.lastSeen, [exercise.id]: new Date().toISOString() };

  // Build weakness queue
  if (!overallCorrect) {
    newStats.sessionErrors = { ...stats.sessionErrors };
    for (const tag of exercise.conceptTags) {
      newStats.sessionErrors[tag] = (newStats.sessionErrors[tag] || 0) + 1;
    }
    // Add similar exercises to weaknessQueue
    // (caller must pass exercises pool to get IDs; done in selectNext)
  }

  return newStats;
}

export function getRecentAccuracy(stats) {
  const recent = stats.recentResults || [];
  if (recent.length === 0) return null;
  const correct = recent.filter(r => r.correct).length;
  return Math.round((correct / recent.length) * 100);
}

export function getWeakestConcepts(stats, topN = 3) {
  const acc = stats.conceptAccuracy || {};
  return Object.entries(acc)
    .filter(([, v]) => v !== null)
    .sort(([, a], [, b]) => a - b)
    .slice(0, topN)
    .map(([tag, score]) => ({ tag, score: Math.round(score * 100) }));
}

// Score an exercise for selection — lower = more likely to pick
function scoreExercise(exercise, stats, recentIds) {
  let score = Math.random() * 0.3; // base randomness

  // Penalize recently seen
  const lastSeen = stats.lastSeen[exercise.id];
  if (lastSeen) {
    const secondsAgo = (Date.now() - new Date(lastSeen).getTime()) / 1000;
    if (secondsAgo < 120) score += 2; // heavily deprioritize recent
    else if (secondsAgo < 300) score += 0.5;
  }

  // Boost exercises matching weak concepts
  const acc = stats.conceptAccuracy || {};
  for (const tag of exercise.conceptTags) {
    const tagAcc = acc[tag];
    if (tagAcc !== null && tagAcc !== undefined) {
      // Lower accuracy → lower score → more likely to pick
      score -= (1 - tagAcc) * 0.8;
    }
    // Boost session errors
    const sessionErr = (stats.sessionErrors || {})[tag] || 0;
    score -= sessionErr * 0.3;
  }

  // Boost if tense accuracy is low
  const tenseAcc = (stats.tenseAccuracy || {})[exercise.expectedTense];
  if (tenseAcc !== null && tenseAcc !== undefined) {
    score -= (1 - tenseAcc) * 0.4;
  }

  // Boost verb family weak exercises
  const family = getVerbFamily(exercise.verb, exercise.expectedTense);
  const familyAcc = (stats.verbFamilyAccuracy || {})[family];
  if (familyAcc !== null && familyAcc !== undefined) {
    score -= (1 - familyAcc) * 0.3;
  }

  return score;
}

export function selectNext(exercises, stats, currentId = null) {
  if (!exercises || exercises.length === 0) return null;

  const pool = exercises.filter(e => e.id !== currentId);
  if (pool.length === 0) return exercises[0];

  // Sort by score (ascending) — lowest score = highest priority
  const scored = pool.map(e => ({ exercise: e, score: scoreExercise(e, stats) }));
  scored.sort((a, b) => a.score - b.score);

  // Pick from top 3 with weighted random to avoid being too deterministic
  const topK = Math.min(3, scored.length);
  const weights = [0.6, 0.3, 0.1].slice(0, topK);
  const totalWeight = weights.reduce((a, b) => a + b, 0);
  let rand = Math.random() * totalWeight;
  for (let i = 0; i < topK; i++) {
    rand -= weights[i];
    if (rand <= 0) return scored[i].exercise;
  }
  return scored[0].exercise;
}

export function normalizeAnswer(str) {
  return str.trim().toLowerCase();
}

export function checkConjugation(input, correct, lenient = false) {
  const a = normalizeAnswer(input);
  const b = normalizeAnswer(correct);
  if (a === b) return true;
  if (lenient) {
    // Only strip accent marks for comparison
    const stripAccents = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    return stripAccents(a) === stripAccents(b);
  }
  return false;
}
