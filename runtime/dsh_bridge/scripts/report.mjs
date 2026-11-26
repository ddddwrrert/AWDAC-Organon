import { readdir, readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'
import { createHash } from 'node:crypto'

const sources = await Promise.all(['regression', 'evidence'].map(name =>
  readFile(new URL('../awdac/' + name + '.js', import.meta.url), 'utf8')))
const { diagnose, merit, outcome, seedPairs, finite } = new Function(
  sources.join('\n') + '\nreturn { diagnose, merit, outcome, seedPairs, finite }',
)()

const load = async path => JSON.parse(await readFile(path, 'utf8'))
const candidateId = /^c[0-9]{6}$/

export async function report(root, program) {
  const rows = (await readFile(join(root, 'population.jsonl'), 'utf8'))
    .split(/\r?\n/).filter(line => line.trim()).map(line => JSON.parse(line))
  const original = new Map(rows.map(row => [row.id, row]))
  const evaluation = new Map()
  for (const row of rows) {
    if (!candidateId.test(row.id)) throw new Error('Invalid candidate ID in population')
    try {
      evaluation.set(row.id, await load(join(root, 'evals', row.id + '.json')))
    } catch (error) {
      if (error.code !== 'ENOENT') throw error
    }
  }

  const allocated = (await readdir(join(root, 'candidates'), { withFileTypes: true }))
    .filter(entry => entry.isDirectory() && candidateId.test(entry.name) && entry.name !== 'c000000')
  const statuses = {}
  const fingerprints = new Set()
  let effective = 0
  const details = []
  for (const row of rows.filter(row => row.parent !== null)) {
    const child = evaluation.get(row.id)
    const parent = evaluation.get(row.parent)
    const status = diagnose(child, parent)
    statuses[status] = (statuses[status] ?? 0) + 1
    const childPath = join(root, 'candidates', row.id, program)
    if (outcome(child) === 'accepted' && finite(row.fitness)) {
      try {
        const hash = createHash('sha256').update(await readFile(childPath)).digest('hex')
        if (!fingerprints.has(hash)) {
          fingerprints.add(hash)
          effective++
        }
      } catch (error) {
        if (error.code !== 'ENOENT') throw error
      }
    }
    const old = original.get(row.parent)?.fitness
    details.push({
      id: row.id, parent: row.parent, fitness: row.fitness, diagnosis: status,
      qMeritDelta: outcome(child) === 'accepted' && outcome(parent) === 'accepted' &&
        finite(old) && finite(row.fitness) ? merit(row.fitness) - merit(old) : null,
      seedPairs: seedPairs(parent?.metrics?.awdac ?? parent?.awdac, child?.metrics?.awdac ?? child?.awdac),
    })
  }
  let best = null
  for (const row of rows) {
    if (finite(row.fitness) && (best === null || merit(row.fitness) > merit(best.fitness))) best = row
  }
  return {
    allocated: allocated.length, completed: details.length, effective, statuses,
    best: best && { id: best.id, fitness: best.fitness },
    feedback: { recordedEvaluations: details.filter(row => evaluation.has(row.id)).length,
      knownOutcomes: details.filter(row => outcome(evaluation.get(row.id)) !== 'unknown').length,
      pairedSeedRows: details.filter(row => row.seedPairs.length > 0).length },
    details,
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [, , root, program] = process.argv
  if (!root || !program) throw new Error('Usage: node scripts/report.mjs RUN_ROOT PROGRAM_RELATIVE_PATH')
  process.stdout.write(JSON.stringify(await report(root, program), null, 2) + '\n')
}
