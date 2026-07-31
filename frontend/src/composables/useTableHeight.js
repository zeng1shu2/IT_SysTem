import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

/**
 * 测量表格容器（.table-area）的可用高度，并把它喂给 <el-table :height>，
 * 让表格 body 在容器内部滚动，而不是把整个页面往下推（整页滚动）。
 *
 * 用法：
 *   <div class="table-area" ref="tableAreaRef">
 *     <el-table :height="tableHeight" ... />
 *   </div>
 *   const tableAreaRef = ref(null)
 *   const { tableHeight } = useTableHeight(tableAreaRef)
 *
 * @param {import('vue').Ref<HTMLElement|null>} wrapperRef  指向 .table-area 的元素 ref
 * @param {{ offset?: number }} [opts]  offset: 额外要扣除的像素（如间隙），默认 0
 */
export function useTableHeight(wrapperRef, opts = {}) {
  const offset = opts.offset || 0
  const tableHeight = ref(320)
  let observer = null
  let fallback = null

  function measure() {
    const el = wrapperRef.value
    if (!el) return
    const h = el.clientHeight - offset
    if (h > 0) tableHeight.value = Math.floor(h)
  }

  onMounted(async () => {
    await nextTick()
    measure()
    if (typeof ResizeObserver !== 'undefined') {
      observer = new ResizeObserver(() => measure())
      if (wrapperRef.value) observer.observe(wrapperRef.value)
    } else {
      fallback = measure
      window.addEventListener('resize', fallback)
    }
  })

  onBeforeUnmount(() => {
    if (observer) observer.disconnect()
    if (fallback) window.removeEventListener('resize', fallback)
  })

  return { tableHeight }
}
