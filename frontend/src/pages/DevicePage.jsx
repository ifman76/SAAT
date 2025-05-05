
import React from 'react';
import { getFilteredQuestions } from '../utils/getRandomQuestions';
import { deviceQuestionsPool } from '../data/allQuestions';

const questions = getFilteredQuestions(deviceQuestionsPool, 'Device', 'Low', 'Human', 6);

export default function DevicePage() {
  return (
    <div>
      <h1>Device Questions</h1>
      <ul>
        {questions.map((q, idx) => (
          <li key={idx}>{q.question}</li>
        ))}
      </ul>
    </div>
  );
}
