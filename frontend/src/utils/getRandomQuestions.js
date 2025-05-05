
export function getFilteredQuestions(pool, section, difficulty, source, count = 5) {
  const filtered = pool.filter(
    q => q.section === section &&
         q.difficulty === difficulty &&
         q.source === source
  );
  const shuffled = filtered.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}
