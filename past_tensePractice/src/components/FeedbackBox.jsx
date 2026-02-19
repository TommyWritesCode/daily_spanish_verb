import styles from './FeedbackBox.module.css';

export default function FeedbackBox({ exercise, selectedTense, userInput, feedback, onNext }) {
  const { classificationCorrect, conjugationCorrect } = feedback;
  const allCorrect = classificationCorrect && conjugationCorrect;

  const tenseLabel = (t) => t === 'PRETERITE' ? '⚡ EVENT (Preterite)' : '🌊 BACKGROUND (Imperfect)';

  return (
    <div className={`${styles.box} ${allCorrect ? styles.allCorrect : styles.hasError}`}>
      {/* Overall result */}
      <div className={styles.resultBadge}>
        {allCorrect ? (
          <span className={styles.correct}>✓ Correct!</span>
        ) : (
          <span className={styles.incorrect}>✗ Not quite</span>
        )}
      </div>

      <div className={styles.grid}>
        {/* Classification result */}
        <div className={styles.item}>
          <span className={styles.itemLabel}>Tense Choice</span>
          <div className={styles.itemRow}>
            <span className={classificationCorrect ? styles.ok : styles.err}>
              {classificationCorrect ? '✓' : '✗'}
            </span>
            <span>
              You: <strong>{tenseLabel(selectedTense)}</strong>
              {!classificationCorrect && (
                <> · Correct: <strong>{tenseLabel(exercise.expectedTense)}</strong></>
              )}
            </span>
          </div>
        </div>

        {/* Conjugation result */}
        <div className={styles.item}>
          <span className={styles.itemLabel}>Conjugation</span>
          <div className={styles.itemRow}>
            <span className={conjugationCorrect ? styles.ok : styles.err}>
              {conjugationCorrect ? '✓' : '✗'}
            </span>
            <span>
              {conjugationCorrect ? (
                <strong className={styles.correctWord}>{exercise.correctForm}</strong>
              ) : (
                <>
                  You typed: <strong className={styles.wrongWord}>{userInput || '(blank)'}</strong>
                  {' · '}Correct: <strong className={styles.correctWord}>{exercise.correctForm}</strong>
                </>
              )}
            </span>
          </div>
        </div>

        {/* Why */}
        <div className={`${styles.item} ${styles.why}`}>
          <span className={styles.itemLabel}>Why?</span>
          <p className={styles.whyText}>{exercise.why}</p>
        </div>

        {/* Timeline */}
        <div className={`${styles.item} ${styles.timeline}`}>
          <span className={styles.itemLabel}>Timeline</span>
          <code className={styles.timelineText}>{exercise.timeline}</code>
        </div>
      </div>

      <button className={styles.nextBtn} onClick={onNext}>
        Next rep →
        <span className={styles.enterHint}>[Enter]</span>
      </button>
    </div>
  );
}
