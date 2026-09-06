const PERSONA_VOICE = {
  intern: { rate: 1.05, pitch: 1.05 },
  professor: { rate: 0.9, pitch: 0.85 },
  journalist: { rate: 1.08, pitch: 1.0 },
  executive: { rate: 1.05, pitch: 0.9 },
}

function textForSpeech(text) {
  return text.replace(/[*#_]/g, ' ').replace(/\s+/g, ' ').trim()
}

export function stopSpeaking() {
  if (typeof window === 'undefined' || !window.speechSynthesis) {
    return
  }
  window.speechSynthesis.cancel()
}

export function speakExplanation(text, persona) {
  stopSpeaking()
  if (!text || typeof window === 'undefined' || !window.speechSynthesis) {
    return
  }

  const settings = PERSONA_VOICE[persona] || PERSONA_VOICE.professor
  const utterance = new SpeechSynthesisUtterance(textForSpeech(text))
  utterance.rate = settings.rate
  utterance.pitch = settings.pitch
  utterance.lang = 'en-US'
  window.speechSynthesis.speak(utterance)
}
