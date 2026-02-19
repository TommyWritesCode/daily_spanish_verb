import styles from './Header.module.css';

const TAG_LABELS = {
  INTERRUPTION: 'Interruption',
  HABIT: 'Habit',
  REPEATED_PAST: 'Repeated',
  DESCRIPTION: 'Description',
  STATE: 'State',
  AGE: 'Age',
  WEATHER: 'Weather',
  TIME: 'Time',
  EVENT_SEQUENCE: 'Sequence',
  COMPLETED_ACTION: 'Completed',
  COUNTED_REPETITION: 'Counted Rep',
  MEANING_CHANGE: 'Meaning Change',
  ONGOING_BACKGROUND: 'Ongoing BG',
};

export default function Header({
  mode, onModeSwitch, repCount, streak, accuracy, weakConcepts,
  lenient, onToggleLenient, onReset,
}) {
  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <span className={styles.logo}>🇪🇸 Past Tense Trainer</span>
        <nav className={styles.modes}>
          <button
            className={`${styles.modeBtn} ${mode === 'PRACTICE' ? styles.active : ''}`}
            onClick={() => onModeSwitch('PRACTICE')}
          >
            Practice
          </button>
          <button
            className={`${styles.modeBtn} ${mode === 'CONTRAST' ? styles.active : ''}`}
            onClick={() => onModeSwitch('CONTRAST')}
          >
            Contrast
          </button>
        </nav>
      </div>

      <div className={styles.stats}>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Reps</span>
          <span className={styles.statValue}>{repCount}</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statLabel}>Streak</span>
          <span className={styles.statValue} style={{ color: streak > 4 ? 'var(--green)' : undefined }}>
            {streak}
          </span>
        </div>
        {accuracy !== null && (
          <div className={styles.stat}>
            <span className={styles.statLabel}>Last 20</span>
            <span
              className={styles.statValue}
              style={{ color: accuracy >= 70 ? 'var(--green)' : accuracy >= 50 ? 'var(--yellow)' : 'var(--red)' }}
            >
              {accuracy}%
            </span>
          </div>
        )}

        {weakConcepts.length > 0 && (
          <div className={styles.weaknesses}>
            {weakConcepts.map(({ tag, score }) => (
              <span key={tag} className={styles.weakTag} title={`${score}% accurate`}>
                {TAG_LABELS[tag] || tag}
                <span className={styles.weakScore}>{score}%</span>
              </span>
            ))}
          </div>
        )}
      </div>

      <div className={styles.right}>
        <button
          className={`${styles.toggle} ${lenient ? styles.on : ''}`}
          onClick={onToggleLenient}
          title="Lenient mode ignores accent marks"
        >
          {lenient ? 'Accents: lenient' : 'Accents: strict'}
        </button>
        <button className={styles.resetBtn} onClick={onReset} title="Reset all progress">
          Reset
        </button>
      </div>
    </header>
  );
}
