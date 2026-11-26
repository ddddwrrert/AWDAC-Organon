import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { pathToFileURL } from 'node:url'

const local = name => readFile(new URL('../' + name, import.meta.url), 'utf8')

export async function build(original, profile) {
  const profiles = JSON.parse(await local('experiments/profiles.json'))
  if (!Object.hasOwn(profiles, profile)) throw new Error('Unknown profile: ' + profile)
  if (profile === 'baseline') throw new Error('Baseline runs with unmodified Organon and no plugin.')
  const source = await readFile(join(original, 'plugins/dsh-evolve-loop/src/providers/mutate.js'), 'utf8')
  const originalProvider = source.replace(/^export (?=(?:async )?function |const )/gm, '')
    .replace(/^export default \{ name, mutate, defaultInstruction, defaultPersona \}\s*$/m, '')
  if (/^export |^import /m.test(originalProvider) || !originalProvider.includes('async function mutate(')) {
    throw new Error('Unsupported Organon mutate provider. Audit the source before building.')
  }
  return [
    'const settings = ' + JSON.stringify(profiles[profile]),
    originalProvider,
    ...await Promise.all(['capability', 'collaboration', 'regression', 'evidence', 'provider']
      .map(name => local('awdac/' + name + '.js'))),
  ].join('\n\n')
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const [, , original, profile = 'full'] = process.argv
  if (!original) throw new Error('Usage: node scripts/build.mjs ORIGINAL_ROOT [profile]')
  process.stdout.write(await build(original, profile))
}
