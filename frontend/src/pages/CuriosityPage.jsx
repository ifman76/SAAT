
import React from 'react';
import { getFilteredQuestions } from '../utils/getRandomQuestions';
import { curiosityQuestionsPool } from '../data/allQuestions';

const questions = getFilteredQuestions(curiosityQuestionsPool, 'Behavior/Curiocity', 'Positive', 'GPT', 6);

export default function CuriosityPage() {
  return (
    <div>
      <h1>Curiosity Questions</h1>
      <ul>
        {questions.map((q, idx) => (
          <li key={idx}>{q.question}</li>
        ))}
      </ul>
    </div>
  );
}
