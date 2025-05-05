
import React from 'react';
import {
  calculateKnowledgeScore,
  calculateDeviceScore,
  calculateBehaviorScore,
  calculateFinalScore
} from '../utils/scoring';

export default function ResultPage({ knowledgeAnswers, deviceAnswers, behaviorAnswers, selectedDevices, certifiedDevices }) {
  const knowledge = calculateKnowledgeScore(knowledgeAnswers);
  const device = calculateDeviceScore(deviceAnswers, certifiedDevices, selectedDevices);
  const behavior = calculateBehaviorScore(behaviorAnswers);
  const finalScore = calculateFinalScore(knowledge, device, behavior);

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">결과 요약 / Final Summary</h2>
      <ul>
        <li>Knowledge: {knowledge.toFixed(1)} / 100</li>
        <li>Device: {device.toFixed(1)} / 100</li>
        <li>Behavior: {behavior.toFixed(1)} / 100</li>
        <li className="mt-2 font-bold">Total: {finalScore.toFixed(1)} / 100</li>
      </ul>
    </div>
  );
}
