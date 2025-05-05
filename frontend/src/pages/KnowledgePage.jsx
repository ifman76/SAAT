
import React from 'react';
import { getFilteredQuestions } from '../utils/getRandomQuestions';
import { knowledgeQuestionsPool } from '../data/allQuestions';

const questions = getFilteredQuestions(knowledgeQuestionsPool, 'Knowledge', 'Medium', 'GPT', 8);

export default function KnowledgePage() {
  return (
    <div>
      <h1>Knowledge Questions</h1>
      <ul>
        {questions.map((q, idx) => (
          <li key={idx}>{q.question}</li>
        ))}
      </ul>
    </div>
  );
}
