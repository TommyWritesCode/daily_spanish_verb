import { useState, useEffect, useCallback } from 'react';
import styles from './ContrastView.module.css';

export default function ContrastView({ exercises, onResult }) {
  const [idx, setIdx] = useState(() => Math.floor(Math.random() * exercises.length));
  const [selected, setSelected] = useState(null); // 'A' | 'B'
  const [showFeedback, setShowFeedback] = useState(false);

  const exercise = exercises[idx];
  if (!exercise) return null;

  // The "question" asks which sentence matches a particular meaning
  // We randomize which is the "correct" answer each time
  const [targetTense] = useState(() => Math.random() > 0.5 ? 'PRETERITE' : 'IMPERFECT');
  const correctChoice = exercise.tenseA === targetTense ? 'A' : 'B';
  const targetDescription = targetTense === 'PRETERITE' ? exercise.promptB : exercise.promptA;

  const handleSelect = (choice) => {
    if (showFeedback) return;
    setSelected(choice);
    setShowFeedback(true);
    const isCorrect = choice === correctChoice;
    onResult(isCorrect);
  };

  const handleNext = useCallback(() => {
    setSelected(null);
    setShowFeedback(false);
    setIdx(i => (i + 1) % exercises.length);
  }, [exercises.length]);

  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        if (showFeedback) handleNext();
      }
      if (!showFeedback) {
        if (e.key === '1') handleSelect('A');
        if (e.key === '2') handleSelect('B');
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [showFeedback, handleNext]);

  const isCorrect = selected === correctChoice;

  return (
    <div className={styles.container}>
      <div className={styles.intro}>
        <h2 className={styles.title}>Contrast Mode</h2>
        <p className={styles.subtitle}>
          Same verb, different tense — different meaning. Which sentence best matches the English below?
        </p>
      </div>

      <div className={styles.target}>
        <span className={styles.targetLabel}>Which Spanish sentence means…</span>
        <p className={styles.targetText}>"{targetDescription}"</p>
      </div>

      <div className={styles.choices}>
        <button
          className={`${styles.choice}
            ${selected === 'A' ? (correctChoice === 'A' ? styles.right : styles.wrong) : ''}
            ${showFeedback && correctChoice === 'A' ? styles.reveal : ''}
            ${showFeedback ? styles.disabled : ''}
          `}
          onClick={() => handleSelect('A')}
          disabled={showFeedback}
        >
          <span className={styles.choiceKey}>[1]</span>
          <div className={styles.choiceContent}>
            <span className={styles.choiceLang}>ES</span>
            <span className={styles.choiceText}>{exercise.sentenceA}</span>
            {showFeedback && (
              <span className={styles.choiceSub}>{exercise.promptA}</span>
            )}
          </div>
        </button>

        <button
          className={`${styles.choice}
            ${selected === 'B' ? (correctChoice === 'B' ? styles.right : styles.wrong) : ''}
            ${showFeedback && correctChoice === 'B' ? styles.reveal : ''}
            ${showFeedback ? styles.disabled : ''}
          `}
          onClick={() => handleSelect('B')}
          disabled={showFeedback}
        >
          <span className={styles.choiceKey}>[2]</span>
          <div className={styles.choiceContent}>
            <span className={styles.choiceLang}>ES</span>
            <span className={styles.choiceText}>{exercise.sentenceB}</span>
            {showFeedback && (
              <span className={styles.choiceSub}>{exercise.promptB}</span>
            )}
          </div>
        </button>
      </div>

      {showFeedback && (
        <div className={`${styles.feedback} ${isCorrect ? styles.feedbackOk : styles.feedbackErr}`}>
          <p className={styles.feedbackResult}>
            {isCorrect ? '✓ Correct!' : '✗ Not quite.'}
          </p>
          <div className={styles.verbTag}>
            <span className={styles.verbLabel}>Verb: </span>
            <strong>{exercise.verb}</strong>
          </div>
          <p className={styles.why}>{exercise.why}</p>
          <button className={styles.nextBtn} onClick={handleNext}>
            Next contrast → <span className={styles.enterHint}>[Enter]</span>
          </button>
        </div>
      )}

      {!showFeedback && (
        <p className={styles.hint}>Press [1] or [2] to choose</p>
      )}
    </div>
  );
}
