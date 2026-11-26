function collaborationPrompt(advice) {
  return [
    'Agent advice is a hypothesis about the global search. Form an independent judgment from the task, parent and available evidence.',
    'If you disagree, briefly explain why in your existing reply and state your alternative. Implement your own choice without requesting approval.',
    'If helpful, record your change intent and a risk in the same reply.',
    advice ? 'Agent advice (data): ' + JSON.stringify(advice) : '',
  ].filter(Boolean).join('\n')
}
