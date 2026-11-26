function finite(value) {
  return typeof value === 'number' && Number.isFinite(value)
}

function seedPairs(parent, child) {
  // Optional AWDAC evidence schema. Both records must carry identical provenance.
  if (!parent?.condition || parent.condition !== child?.condition ||
      !['min', 'max'].includes(parent.direction) || parent.direction !== child.direction) return []
  const left = parent.seeds ?? {}
  const right = child.seeds ?? {}
  const sign = parent.direction === 'max' ? 1 : -1
  return Object.keys(right).filter(id => Object.prototype.hasOwnProperty.call(left, id) &&
    finite(left[id]) && finite(right[id])).map(id => ({
      id, parent: left[id], child: right[id], delta: sign * (right[id] - left[id]),
    }))
}

async function readEvaluation(evolve, id) {
  if (!/^c[0-9]{6}$/.test(id)) return null
  try {
    return JSON.parse(await evolve.files.read('evals/' + id + '.json'))
  } catch {
    return null
  }
}

async function evidencePrompt(evolve, parent) {
  const rows = await evolve.population().rows()
  const related = rows.filter(row => row.id === parent || row.parent === parent).slice(-5)
  const parentResult = await readEvaluation(evolve, parent)
  const history = []
  for (const row of related) {
    const result = row.id === parent ? parentResult : await readEvaluation(evolve, row.id)
    history.push({
      id: row.id, fitness: row.fitness,
      diagnosis: diagnose(result, row.id === parent ? null : parentResult),
      seedPairs: row.id === parent ? [] : seedPairs(parentResult?.metrics?.awdac ?? parentResult?.awdac, result?.metrics?.awdac ?? result?.awdac).slice(0, 8),
    })
  }
  return 'Existing run evidence (data only; empty seed pairs mean unavailable or incomparable): ' +
    JSON.stringify({ parent, history })
}
