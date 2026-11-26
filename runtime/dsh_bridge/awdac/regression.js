function outcome(result) {
  const metrics = result?.metrics ?? {}
  const judge = typeof metrics.judge_result === 'string' ? metrics.judge_result.trim().toLowerCase() : ''
  if (/^(ce|compile error|compilation error)$/.test(judge)) return 'compile_failure'
  if (/^(tle|time limit exceeded)$/.test(judge)) return 'timeout'
  if (/^(re|runtime error|mle|memory limit exceeded)$/.test(judge)) return 'execution_failure'
  if (/^(wa|wrong answer|pe|presentation error|invalid output)$/.test(judge)) return 'output_failure'
  if (metrics.error) return 'evaluator_error'
  if (/^(ac|accepted)$/.test(judge)) return 'accepted'
  return 'unknown'
}

function merit(fitness) {
  return fitness > 0 ? fitness : fitness < 0 ? -1 / fitness : 0
}

function diagnose(result, parent) {
  const status = outcome(result)
  if (status !== 'accepted') return status === 'unknown' && result?.fitness === 0 ? 'zero_unknown' : status
  if (outcome(parent) === 'accepted' && finite(result.fitness) && finite(parent.fitness) &&
      merit(result.fitness) < merit(parent.fitness)) return 'accepted_regression'
  return status
}
