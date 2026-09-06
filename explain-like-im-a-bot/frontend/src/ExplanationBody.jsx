function splitInline(text) {
  const parts = []
  const pattern = /\*\*(.+?)\*\*|\*(.+?)\*/g
  let lastIndex = 0
  let match

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', value: text.slice(lastIndex, match.index) })
    }
    parts.push({ type: 'strong', value: match[1] || match[2] })
    lastIndex = match.index + match[0].length
  }

  if (lastIndex < text.length) {
    parts.push({ type: 'text', value: text.slice(lastIndex) })
  }

  return parts.map((part, index) => {
    const cleaned = part.value.replace(/[*#_]+/g, '').replace(/[ \t]+\n/g, '\n')
    if (!cleaned) {
      return null
    }
    if (part.type === 'strong') {
      return <strong key={index}>{cleaned}</strong>
    }
    return <span key={index}>{cleaned}</span>
  })
}

export function ExplanationBody({ text }) {
  const blocks = text
    .replace(/\r\n/g, '\n')
    .split(/\n{2,}/)
    .map((block) => block.replace(/^\s*[-*]\s+/gm, '').trim())
    .filter(Boolean)

  return (
    <div className="body">
      {blocks.map((block, index) => (
        <p key={index}>{splitInline(block)}</p>
      ))}
    </div>
  )
}
