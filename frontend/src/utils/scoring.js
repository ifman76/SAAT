
export function calculateKnowledgeScore(answers) {
  let totalWeighted = 0;
  let totalWeight = 0;
  answers.forEach(ans => {
    let weight = ans.difficulty === 'Low' ? 1 : ans.difficulty === 'Medium' ? 1.5 : 2;
    totalWeight += weight;
    if (ans.correct) totalWeighted += weight;
  });
  return totalWeight === 0 ? 0 : (totalWeighted / totalWeight) * 100;
}

export function calculateDeviceScore(answers, certifiedDevices, selectedDevices) {
  let totalWeighted = 0;
  let totalWeight = 0;
  answers.forEach(ans => {
    let weight = ans.difficulty === 'Low' ? 1 : ans.difficulty === 'Medium' ? 1.5 : 2;
    totalWeight += weight;
    if (ans.correct) totalWeighted += weight;
  });

  const certifiedSet = new Set(certifiedDevices.map(d => `${d.maker}-${d.product}`));
  let matched = selectedDevices.filter(dev => certifiedSet.has(`${dev.maker}-${dev.product}`)).length;
  const bonus = matched >= 2 ? 4 : matched >= 1 ? 2 : 0;
  return totalWeight === 0 ? 0 : ((totalWeighted + bonus) / (totalWeight + 4)) * 100;
}

export function calculateBehaviorScore(answers) {
  const converted = answers.map(ans =>
    ans.direction === 'Positive' ? ans.score : 6 - ans.score
  );
  const sum = converted.reduce((acc, v) => acc + v, 0);
  return (sum / (answers.length * 5)) * 100;
}

export function calculateFinalScore(k, d, b) {
  return (k * 0.4) + (d * 0.3) + (b * 0.3);
}
