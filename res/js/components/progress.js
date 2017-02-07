import bel from 'bel'
import { $ } from 'luett'

function createContainer(description) {
  return bel`
<div class="progress-container">
    <div class="progress-description">${description}</div>
    <div class="progress-bar">
        <div class="progress-track"></div>    
    </div>
</div>
`
}

export default opts => {
  const el = createContainer(opts.description || "", opts.fixed || true)
  const track = $('.progress-track', el)

  return {
    el,
    setProgress(progress) {
      track.style.transform = `scaleX(${progress / 100})`
    },
    remove() {}
  }
}
