import test from 'node:test'
import assert from 'node:assert/strict'
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { build } from '../scripts/build.mjs'
import { report } from '../scripts/report.mjs'

const original = process.env.ORGANON_ORIGINAL ?? fileURLToPath(new URL('../../../Organon_original', import.meta.url))

test('full profile uses one original allocation and worker call with evidence and independent judgment', async () => {
  const plugin = new Function(await build(original, 'full'))()
  let provider
  plugin.apply({
    effect: fn => fn(),
    evolve: { register(slot, value) { assert.equal(slot, 'mutate'); provider = value } },
  })
  const calls = []
  const written = []
  const candidate = { id: 'c000002', dir: 'candidate' }
  const child = await provider.mutate({ parent: 'c000000', model: 'original-model' }, {
    population: () => ({ rows: async () => [
      { id: 'c000000', parent: null, fitness: 100 },
      { id: 'c000001', parent: 'c000000', fitness: 0 },
    ] }),
    files: { async read(path) {
      if (path === 'awdac/agent-advice.txt') return 'Try a smaller neighborhood.'
      return JSON.stringify(path.includes('c000000') ?
        { fitness: 100, metrics: { judge_result: 'AC' } } :
        { fitness: 0, metrics: { judge_result: 'CE' } })
    }, async write(path, data) { written.push([path, JSON.parse(data)]) } },
    async allocate(parent) { calls.push(['allocate', parent]); return candidate },
    async spawnWorker(dir, prompt, options) { calls.push(['worker', dir, prompt, options]); return { text: 'AWDAC_INTENT: {"mode":"radical"}' } },
  })
  assert.equal(child, candidate)
  assert.deepEqual(written, [['awdac/intents/c000002.json', { parent: 'c000000', intent: { mode: 'radical' } }]])
  assert.equal(calls.length, 2)
  assert.deepEqual(calls[0], ['allocate', 'c000000'])
  assert.equal(calls[1][3].model, 'original-model')
  for (const phrase of ['#EVOLVE_START', 'official fitness was 100', 'compile_failure',
    'Try a smaller neighborhood', 'If you disagree', 'complete rewrite']) {
    assert.ok(calls[1][2].includes(phrase), phrase)
  }
})

test('each ablation assembles and the baseline requires no provider', async () => {
  for (const profile of ['acu', 'collaboration', 'evidence']) {
    assert.equal(new Function(await build(original, profile))().name, 'awdac-organon')
  }
  await assert.rejects(build(original, 'baseline'), /unmodified Organon/)
})

test('reports observed budget, regression, paired seed direction and unavailable verdicts', async () => {
  const root = await mkdtemp(join(tmpdir(), 'awdac-test-'))
  try {
    await mkdir(join(root, 'evals'))
    const rows = [
      { id: 'c000000', parent: null, fitness: -10 },
      { id: 'c000001', parent: 'c000000', fitness: -20 },
      { id: 'c000002', parent: 'c000000', fitness: 0 },
    ]
    await writeFile(join(root, 'population.jsonl'), rows.map(row => JSON.stringify(row)).join('\n'))
    for (const row of rows) {
      await mkdir(join(root, 'candidates', row.id), { recursive: true })
      await writeFile(join(root, 'candidates', row.id, 'solution.cpp'), row.id)
    }
    await mkdir(join(root, 'candidates', 'c000003'))
    for (const [id, score] of [['c000000', 10], ['c000001', 20]]) {
      await writeFile(join(root, 'evals', id + '.json'), JSON.stringify({
        fitness: -score, metrics: { judge_result: 'Accepted' },
        awdac: { condition: 'same-task/config', direction: 'min', seeds: { '17': score } },
      }))
    }
    const result = await report(root, 'solution.cpp')
    assert.equal(result.allocated, 3)
    assert.equal(result.completed, 2)
    assert.equal(result.effective, 1)
    assert.equal(result.statuses.accepted_regression, 1)
    assert.equal(result.statuses.unknown, 1)
    assert.equal(result.details[0].seedPairs[0].delta, -10)
    assert.equal(result.details[1].qMeritDelta, null)
    assert.equal(result.best.id, 'c000000')
  } finally {
    await rm(root, { recursive: true, force: true })
  }
})
