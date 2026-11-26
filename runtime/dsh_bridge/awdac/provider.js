function observeWorker(evolve, parent) {
  let id
  const overrides = {
    async allocate(...args) {
      const candidate = await evolve.allocate(...args)
      id = candidate.id
      return candidate
    },
    async spawnWorker(...args) {
      const reply = await evolve.spawnWorker(...args)
      const match = reply?.text?.match(/(?:^|\n)AWDAC_INTENT: *(\{[^\r\n]+\})/u)
      if (match && match[1].length <= 8192 && /^c[0-9]{6}$/.test(id)) {
        try {
          const intent = JSON.parse(match[1])
          await evolve.files.write('awdac/intents/' + id + '.json',
            JSON.stringify({ parent, intent }) + '\n')
        } catch { /* Optional evidence must not affect original variation. */ }
      }
      return reply
    },
  }
  return new Proxy(evolve, {
    get(target, key) {
      if (Object.prototype.hasOwnProperty.call(overrides, key)) return overrides[key]
      const value = Reflect.get(target, key)
      return typeof value === 'function' ? value.bind(target) : value
    },
  })
}

return {
  name: 'awdac-organon',
  inject: ['evolve'],
  apply(ctx) {
    ctx.effect(() => ctx.evolve.register('mutate', {
      name: 'awdac-worker-context',
      async mutate(options, evolve) {
        const parent = options?.parent
        if (!parent) return mutate(options, evolve)
        let extra = ''
        if (settings.evidence) {
          try { extra = await evidencePrompt(evolve, parent) } catch {
            extra = 'Existing run evidence is unavailable.'
          }
        }
        let advice = ''
        if (settings.collaboration) {
          try {
            advice = (await evolve.files.read('awdac/agent-advice.txt')).slice(0, 1600)
          } catch { /* Agent advice is optional. */ }
        }
        const instructions = [
          settings.capability ? capabilityPrompt : '',
          settings.collaboration ? collaborationPrompt(advice) : '',
          extra,
        ].filter(Boolean)
        if (instructions.length === 0) return mutate(options, evolve)
        let fitness = options.parentFitness
        if (fitness === undefined) {
          fitness = (await evolve.population().rows()).find(row => row.id === parent)?.fitness
        }
        const original = options.instruction ?? defaultInstruction(fitness)
        if (settings.collaboration) instructions.push(
          'In your existing final reply, optionally include one line AWDAC_INTENT: followed by a JSON object with mode (incremental, structural, radical), hypothesis, observation, design, benefit, risk, validation, rebuttal and operator_actions (array).')
        return mutate({ ...options, parentFitness: fitness,
          instruction: [original, ...instructions].join('\n\n') }, settings.collaboration ? observeWorker(evolve, parent) : evolve)
      },
    }))
  },
}
