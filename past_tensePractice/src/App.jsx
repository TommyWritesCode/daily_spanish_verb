import { useState, useEffect, useCallback } from 'react';
import exerciseData from './data/exercises.json';
import {
  loadStats, saveStats, clearStats,
  recordResult, selectNext, checkConjugation,
  getRecentAccuracy, getWeakestConcepts,
} from './engine/adaptive.js';
import Header from './components/Header.jsx';
import PracticeView from './components/PracticeView.jsx';
import ContrastView from './components/ContrastView.jsx';
import styles from './App.module.css';

const MODES = { PRACTICE: 'PRACTICE', CONTRAST: 'CONTRAST' };

export default function App() {
  const [mode, setMode] = useState(MODES.PRACTICE);
  const [stats, setStats] = useState(() => loadStats());
  const [currentExercise, setCurrentExercise] = useState(null);
  const [contrastIdx, setContrastIdx] = useState(0);
  const [phase, setPhase] = useState('classify'); // classify | conjugate | feedback
  const [selectedTense, setSelectedTense] = useState(null);
  const [userInput, setUserInput] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [lenient, setLenient] = useState(false);
  const [showHint, setShowHint] = useState(false);

  // Load first exercise
  useEffect(() => {
    const ex = selectNext(exerciseData.practice, stats, null);
    setCurrentExercise(ex);
  }, []); // eslint-disable-line

  const practiceAccuracy = getRecentAccuracy(stats);
  const weakConcepts = getWeakestConcepts(stats, 3);

  const handleModeSwitch = (newMode) => {
    setMode(newMode);
    setPhase('classify');
    setSelectedTense(null);
    setUserInput('');
    setFeedback(null);
    setShowHint(false);
    if (newMode === MODES.CONTRAST) {
      setContrastIdx(0);
    }
  };

  const handleClassify = (tense) => {
    setSelectedTense(tense);
    setPhase('conjugate');
    setShowHint(false);
  };

  const handleSubmit = useCallback(() => {
    if (!currentExercise || phase !== 'conjugate') return;
    const classificationCorrect = selectedTense === currentExercise.expectedTense;
    const conjugationCorrect = checkConjugation(userInput, currentExercise.correctForm, lenient);
    const newStats = recordResult(stats, currentExercise, classificationCorrect, conjugationCorrect);
    saveStats(newStats);
    setStats(newStats);
    setFeedback({ classificationCorrect, conjugationCorrect });
    setPhase('feedback');
  }, [currentExercise, phase, selectedTense, userInput, lenient, stats]);

  const handleNext = () => {
    const next = selectNext(exerciseData.practice, stats, currentExercise?.id);
    setCurrentExercise(next);
    setPhase('classify');
    setSelectedTense(null);
    setUserInput('');
    setFeedback(null);
    setShowHint(false);
  };

  const handleContrastResult = (wasCorrect) => {
    // Track contrast results in tenseAccuracy loosely
    const updated = { ...stats };
    updated.recentResults = [{ correct: wasCorrect }, ...(updated.recentResults || [])].slice(0, 20);
    updated.totalReps = (updated.totalReps || 0) + 1;
    if (wasCorrect) updated.streak = (updated.streak || 0) + 1;
    else updated.streak = 0;
    saveStats(updated);
    setStats(updated);
  };

  const handleReset = () => {
    if (window.confirm('Reset all progress? This cannot be undone.')) {
      clearStats();
      setStats(loadStats());
    }
  };

  return (
    <div className={styles.app}>
      <Header
        mode={mode}
        onModeSwitch={handleModeSwitch}
        repCount={stats.totalReps || 0}
        streak={stats.streak || 0}
        accuracy={practiceAccuracy}
        weakConcepts={weakConcepts}
        lenient={lenient}
        onToggleLenient={() => setLenient(l => !l)}
        onReset={handleReset}
      />

      <main className={styles.main}>
        {mode === MODES.PRACTICE ? (
          <PracticeView
            exercise={currentExercise}
            phase={phase}
            selectedTense={selectedTense}
            userInput={userInput}
            feedback={feedback}
            showHint={showHint}
            onClassify={handleClassify}
            onInputChange={setUserInput}
            onSubmit={handleSubmit}
            onNext={handleNext}
            onShowHint={() => setShowHint(true)}
          />
        ) : (
          <ContrastView
            exercises={exerciseData.contrast}
            onResult={handleContrastResult}
          />
        )}
      </main>
    </div>
  );
}
