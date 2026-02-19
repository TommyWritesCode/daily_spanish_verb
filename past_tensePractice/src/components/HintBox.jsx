import styles from './HintBox.module.css';

const CONCEPT_HINTS = {
  INTERRUPTION: 'Two actions: one was ongoing → imperfect. One happened suddenly → preterite.\n"Yo _____ cuando [evento]."',
  HABIT: 'Repeated in the past? Use imperfect.\nLook for: siempre, cada día, todos los veranos, de niño…',
  REPEATED_PAST: 'If it repeated without a count, it\'s imperfect.\nIf there\'s a number ("3 times"), it\'s preterite.',
  DESCRIPTION: 'Describing a state, feeling, age, time, or weather? Imperfect.\nAsking "what was it like?" → imperfect.',
  STATE: 'States of mind/body (querer, saber, poder, tener) are usually imperfect.\nUnless the state was completed/changed at a moment.',
  AGE: 'Age is always a description → imperfect.\n"Tenía X años" = I was X years old.',
  WEATHER: 'Weather as background/context → imperfect.\n"Llovía" = it was raining (ongoing).',
  TIME: 'Telling the time → imperfect.\n"Eran las tres" = it was 3 o\'clock.',
  EVENT_SEQUENCE: 'List of completed events in order? Preterite.\nPrimero X, luego Y, después Z.',
  COMPLETED_ACTION: 'Did it happen, start, or end at a specific point? Preterite.\n"Ayer", "en 1999", a specific moment.',
  COUNTED_REPETITION: 'If you can count it ("dos veces", "tres veces"), preterite.\nIf it\'s unbounded ("muchas veces", "siempre"), imperfect.',
  MEANING_CHANGE: 'This verb changes meaning with tense!\nImperfect = state. Preterite = event/change.',
  ONGOING_BACKGROUND: 'This is the continuous "background" action.\nWhat was already happening when something else occurred?',
};

const ENDING_TABLES = {
  AR_IMP: { label: '-AR Imperfect', endings: 'yo: -aba · tú: -abas · él: -aba\nnos: -ábamos · ellos: -aban' },
  ERIR_IMP: { label: '-ER/-IR Imperfect', endings: 'yo: -ía · tú: -ías · él: -ía\nnos: -íamos · ellos: -ían' },
  AR_PRET: { label: '-AR Preterite', endings: 'yo: -é · tú: -aste · él: -ó\nnos: -amos · ellos: -aron' },
  ERIR_PRET: { label: '-ER/-IR Preterite', endings: 'yo: -í · tú: -iste · él: -ió\nnos: -imos · ellos: -ieron' },
};

function getVerbFamily(verb, tense) {
  const isAR = verb.endsWith('ar');
  if (tense === 'PRETERITE') return isAR ? 'AR_PRET' : 'ERIR_PRET';
  return isAR ? 'AR_IMP' : 'ERIR_IMP';
}

export default function HintBox({ exercise }) {
  const family = getVerbFamily(exercise.verb, exercise.expectedTense);
  const endingInfo = ENDING_TABLES[family];

  // Get the most relevant concept hint
  const primaryTag = exercise.conceptTags.find(t => CONCEPT_HINTS[t]) || exercise.conceptTags[0];
  const conceptHint = CONCEPT_HINTS[primaryTag];

  return (
    <div className={styles.box}>
      <div className={styles.section}>
        <h4 className={styles.label}>Tense Rule</h4>
        <p className={styles.hint}>{conceptHint || 'Think: is this a completed event, or ongoing background?'}</p>
      </div>
      {endingInfo && (
        <div className={styles.section}>
          <h4 className={styles.label}>{endingInfo.label} Endings</h4>
          <pre className={styles.endings}>{endingInfo.endings}</pre>
        </div>
      )}
    </div>
  );
}
