import { $, toggleClass } from 'luett';
import closest from 'closest'

function on(el, event, callback, useCapture = false) {
  el.addEventListener(event, callback, useCapture)
  return {
    destroy: () => el.removeEventListener(event, callback, useCapture)
  }
}

export default el => {
  const authorSelect = $('[data-select-type="author"]', el);
  const pinnedCheck = $('input[name="pinned"]', el);
  const pinnedWrap = closest(pinnedCheck, ".form-group");

  if(!authorSelect || !pinnedWrap) {
    return {
      remove: () => {}
    }
  }

  function setState () {
    toggleClass(pinnedWrap, "form-group-unused", !authorSelect.value)
  }

  const authorSelectListener = on(authorSelect, "change", setState)
  setState()

  return {
    remove: () => {
      authorSelectListener.destroy();
    }
  }
}
