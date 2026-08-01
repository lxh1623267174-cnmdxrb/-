<template>
  <div class="app-shell">
    <!-- ======== Sidebar ======== -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <button class="btn-icon" title="新对话" @click="newChat">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
        </button>
        <span v-if="!sidebarCollapsed" class="sidebar-title">对话历史</span>
        <button class="btn-icon" :title="sidebarCollapsed ? '展开' : '收起'" @click="sidebarCollapsed = !sidebarCollapsed">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <polyline v-if="sidebarCollapsed" points="9,18 15,12 9,6"/>
            <polyline v-else points="15,18 9,12 15,6"/>
          </svg>
        </button>
      </div>

      <div v-if="!sidebarCollapsed" class="sidebar-list">
        <div
          v-for="(chat, idx) in chatHistory"
          :key="chat.id"
          class="chat-item"
          :class="{ active: chat.id === activeChatId }"
          @click="switchChat(chat.id)"
        >
          <span class="chat-item-title">{{ chat.title }}</span>
          <button class="btn-delete" title="删除" @click.stop="deleteChat(chat.id)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <polyline points="3,6 5,6 21,6"/><path d="M19,6v14a2,2,0,0,1-2,2H7a2,2,0,0,1-2-2V6M8,6V4a2,2,0,0,1,2-2h4a2,2,0,0,1,2,2V6"/>
            </svg>
          </button>
        </div>
        <p v-if="chatHistory.length === 0" class="sidebar-empty">暂无对话记录</p>
      </div>
    </aside>

    <!-- ======== Main Chat Area ======== -->
    <main class="chat-main">
      <!-- Header -->
      <header class="chat-header">
        <div class="header-left">
          <button v-if="sidebarCollapsed" class="btn-icon" title="展开侧栏" @click="sidebarCollapsed = false">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <rect x="3" y="3" width="18" height="18" rx="2"/><line x1="9" y1="3" x2="9" y2="21"/>
            </svg>
          </button>
          <span class="header-title">AI 知识库助手</span>
        </div>
        <div class="header-right">
          <button v-if="messages.length > 0" class="btn-text" @click="newChat">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            新对话
          </button>
        </div>
      </header>

      <!-- Messages -->
      <div ref="messagesContainer" class="messages-area">
        <!-- Welcome -->
        <div v-if="messages.length === 0" class="welcome">
          <div class="welcome-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
              <path d="M8 9h8" opacity="0.5"/><path d="M8 13h5" opacity="0.3"/>
            </svg>
          </div>
          <h1 class="welcome-heading">你好，我是 AI 知识库助手</h1>
          <p class="welcome-sub">专注解答奖学金申请、综测评定相关问题</p>
          <div class="welcome-hints">
            <button
              v-for="hint in welcomeHints"
              :key="hint"
              class="hint-chip"
              @click="sendHint(hint)"
            >{{ hint }}</button>
          </div>
        </div>

        <!-- Message bubbles -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message-row"
          :class="msg.role"
        >
          <div class="msg-avatar">
            <template v-if="msg.role === 'user'">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
              </svg>
            </template>
            <template v-else>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2a4 4 0 0 1 4 4v1h2a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h2V6a4 4 0 0 1 4-4z"/>
                <circle cx="12" cy="13" r="2" opacity="0.6"/>
              </svg>
            </template>
          </div>

          <div class="msg-body">
            <div class="msg-bubble">
              <!-- Streaming: raw text + cursor -->
              <template v-if="msg.streaming">
                <div class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
                <span class="typing-cursor">|</span>
              </template>
              <!-- Complete: rendered markdown -->
              <template v-else>
                <div class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
              </template>
            </div>

            <!-- Actions row -->
            <div v-if="!msg.streaming && msg.content" class="msg-actions">
              <button class="btn-action" title="复制" @click="copyMessage(msg.content)">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                  <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Loading indicator when waiting for first token -->
        <div v-if="isWaiting" class="message-row assistant">
          <div class="msg-avatar">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
              <path d="M12 2a4 4 0 0 1 4 4v1h2a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h2V6a4 4 0 0 1 4-4z"/>
            </svg>
          </div>
          <div class="msg-body">
            <div class="msg-bubble thinking">
              <span class="dot-pulse"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input area -->
      <div class="input-area">
        <div class="input-wrapper">
          <textarea
            ref="inputEl"
            v-model="question"
            class="chat-input"
            placeholder="输入问题，Enter 发送，Shift+Enter 换行"
            rows="1"
            :disabled="isStreaming"
            @keydown="onKeydown"
            @input="autoResize"
          ></textarea>
          <button
            v-if="isStreaming"
            class="btn-stop"
            title="停止生成"
            @click="stopStreaming"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <rect x="4" y="4" width="16" height="16" rx="2"/>
            </svg>
          </button>
          <button
            v-else
            class="btn-send"
            :disabled="!question.trim()"
            title="发送"
            @click="send"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <line x1="12" y1="19" x2="12" y2="5"/><polyline points="5,12 12,5 19,12"/>
            </svg>
          </button>
        </div>
        <p class="input-hint">AI 回答仅供参考，请以学校官方文件为准</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/atom-one-dark.css'

// ========== Markdown Config ==========
marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
})

function renderMarkdown(text) {
  if (!text) return ''
  try {
    return marked.parse(text)
  } catch {
    return text.replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }
}

// ========== State ==========
const question = ref('')
const messages = ref([])
const isStreaming = ref(false)
const isWaiting = ref(false) // true between send and first token
const sidebarCollapsed = ref(false)
const messagesContainer = ref(null)
const inputEl = ref(null)

// Abort controller for stopping streams
let abortController = null

// Chat history (simple in-memory, clear on refresh)
const chatHistory = ref([])
const activeChatId = ref(genId())
let historySaveTimer = null

function genId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
}

// ========== Welcome Hints ==========
const welcomeHints = [
  '国家奖学金申请条件是什么？',
  '综测加分项目有哪些？',
  '奖学金的评定流程是怎样的？',
  '如何提高综测成绩？',
]

// ========== Auto Resize ==========
function autoResize() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

// ========== Keyboard ==========
function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

// ========== Scroll to Bottom ==========
async function scrollToBottom(smooth = true) {
  await nextTick()
  const el = messagesContainer.value
  if (!el) return
  el.scrollTo({
    top: el.scrollHeight,
    behavior: smooth ? 'smooth' : 'instant',
  })
}

// ========== Save Chat Title ==========
function saveChatTitle() {
  const userMsg = messages.value.find(m => m.role === 'user')
  const title = userMsg ? userMsg.content.slice(0, 30) + (userMsg.content.length > 30 ? '...' : '') : '新对话'

  const existing = chatHistory.value.find(c => c.id === activeChatId.value)
  if (existing) {
    existing.title = title
  } else if (messages.value.length > 0) {
    chatHistory.value.unshift({ id: activeChatId.value, title })
  }
}

// ========== Send ==========
async function send() {
  const q = question.value.trim()
  if (!q || isStreaming.value) return

  question.value = ''
  // Reset textarea height
  if (inputEl.value) {
    inputEl.value.style.height = 'auto'
  }

  messages.value.push({ role: 'user', content: q, streaming: false })
  messages.value.push({ role: 'assistant', content: '', streaming: true })

  // First user message -> auto-save to history
  if (messages.value.filter(m => m.role === 'user').length === 1) {
    saveChatTitle()
  }

  await scrollToBottom()

  const aiIndex = messages.value.length - 1
  isStreaming.value = true
  isWaiting.value = true

  abortController = new AbortController()

  try {
    const response = await fetch('http://127.0.0.1:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: q }),
      signal: abortController.signal,
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    isWaiting.value = false

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      let text = decoder.decode(value, { stream: true })
      // Strip SSE protocol tokens
      text = text.replace(/data:\s*/g, '').replace(/\n\n/g, '').replace(/\n/g, '')

      messages.value[aiIndex].content += text
      await scrollToBottom()
    }
  } catch (err) {
    if (err.name !== 'AbortError') {
      messages.value[aiIndex].content += `\n\n> ⚠️ 请求失败：${err.message}`
    }
  } finally {
    messages.value[aiIndex].streaming = false
    isStreaming.value = false
    isWaiting.value = false
    abortController = null
    await nextTick()
    // Re-render once more to ensure markdown is finalized
  }
}

function sendHint(hint) {
  question.value = hint
  send()
}

// ========== Stop Streaming ==========
function stopStreaming() {
  if (abortController) {
    abortController.abort()
    abortController = null
  }
}

// ========== Copy ==========
async function copyMessage(text) {
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    // Fallback
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
  }
}

// ========== Chat Management ==========
function newChat() {
  if (isStreaming.value) stopStreaming()
  messages.value = []
  activeChatId.value = genId()
  sidebarCollapsed.value = false
  // Focus input
  nextTick(() => inputEl.value?.focus())
}

function switchChat(id) {
  // Simple demo: just show alert (full persistence needs backend)
  // For now, just set as active
  activeChatId.value = id
}

function deleteChat(id) {
  chatHistory.value = chatHistory.value.filter(c => c.id !== id)
  if (activeChatId.value === id) {
    newChat()
  }
}

// ========== Auto-scroll on new messages ==========
watch(
  () => messages.value.length,
  () => scrollToBottom(false)
)
</script>

<style scoped>
/* ========== Shell Layout ========== */
.app-shell {
  display: flex;
  height: 100%;
  background: var(--bg-primary);
}

/* ========== Sidebar ========== */
.sidebar {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  transition: width var(--duration-normal) var(--ease-out);
  overflow: hidden;
}
.sidebar.collapsed {
  width: 52px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 12px;
  border-bottom: 1px solid var(--border);
}

.sidebar-title {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
}

.sidebar-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.chat-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary);
  transition: background var(--duration-fast) var(--ease-in-out);
}
.chat-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
.chat-item.active {
  background: var(--accent-dim);
  color: var(--accent-light);
}

.chat-item-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-delete {
  opacity: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 4px;
  transition: opacity var(--duration-fast), color var(--duration-fast);
}
.chat-item:hover .btn-delete {
  opacity: 1;
}
.btn-delete:hover {
  color: var(--error);
  background: rgba(239, 68, 68, 0.1);
}

.sidebar-empty {
  padding: 16px;
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
}

/* ========== Main Chat ========== */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--bg-primary);
}

/* ========== Header ========== */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  background: var(--bg-primary);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ========== Buttons ========== */
.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--duration-fast) var(--ease-in-out);
}
.btn-icon:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.btn-text {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-family: var(--font-sans);
  transition: all var(--duration-fast) var(--ease-in-out);
}
.btn-text:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-light);
}

.btn-action {
  display: inline-flex;
  align-items: center;
  padding: 3px 6px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: 4px;
  transition: color var(--duration-fast);
}
.btn-action:hover {
  color: var(--text-secondary);
}

/* ========== Messages Area ========== */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  scroll-behavior: smooth;
}

/* ========== Welcome ========== */
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-dim);
  border-radius: var(--radius-lg);
  color: var(--accent-light);
  margin-bottom: 24px;
}

.welcome-heading {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.welcome-sub {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 32px;
}

.welcome-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 500px;
}

.hint-chip {
  padding: 8px 18px;
  border: 1px solid var(--border);
  background: var(--bg-surface);
  color: var(--text-secondary);
  border-radius: var(--radius-full);
  font-size: 13px;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-in-out);
}
.hint-chip:hover {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent-light);
}

/* ========== Message Row ========== */
.message-row {
  display: flex;
  gap: 12px;
  padding: 12px 20px;
  max-width: 820px;
  margin: 0 auto;
  width: 100%;
  animation: fadeIn 0.3s var(--ease-out);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.message-row.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  margin-top: 2px;
}
.message-row.user .msg-avatar {
  background: var(--accent-dim);
  color: var(--accent-light);
}
.message-row.assistant .msg-avatar {
  background: var(--bg-surface);
  color: var(--text-secondary);
}

.msg-body {
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.message-row.user .msg-body {
  align-items: flex-end;
}

/* ========== Message Bubble ========== */
.msg-bubble {
  padding: 12px 18px;
  border-radius: var(--radius-md);
  font-size: 14.5px;
  line-height: 1.7;
  color: var(--text-primary);
  position: relative;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.message-row.user .msg-bubble {
  background: var(--user-bubble);
  border-bottom-right-radius: 4px;
}

.message-row.assistant .msg-bubble {
  background: var(--assistant-bubble);
  border: 1px solid var(--assistant-border);
  border-bottom-left-radius: 4px;
}

.msg-bubble.thinking {
  padding: 16px 20px;
}

/* ========== Typing Indicator ========== */
.typing-cursor {
  display: inline-block;
  color: var(--accent-light);
  animation: blink 1s step-end infinite;
  font-weight: 100;
  margin-left: 2px;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0; }
}

/* Dot pulse (waiting for first token) */
.dot-pulse {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: pulse 1.4s ease-in-out infinite;
  position: relative;
}
.dot-pulse::before,
.dot-pulse::after {
  content: '';
  position: absolute;
  top: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--text-muted);
}
.dot-pulse::before {
  left: -16px;
  animation: pulse 1.4s ease-in-out 0.2s infinite;
}
.dot-pulse::after {
  left: 16px;
  animation: pulse 1.4s ease-in-out 0.4s infinite;
}

@keyframes pulse {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40%           { transform: scale(1);   opacity: 1; }
}

/* ========== Message Actions ========== */
.msg-actions {
  display: flex;
  gap: 4px;
  margin-top: 4px;
  padding: 0 4px;
}

/* ========== Input Area ========== */
.input-area {
  flex-shrink: 0;
  padding: 12px 20px 16px;
  background: var(--bg-primary);
  border-top: 1px solid var(--border);
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  max-width: 820px;
  margin: 0 auto;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 6px 8px 6px 16px;
  transition: border-color var(--duration-fast) var(--ease-in-out);
}
.input-wrapper:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-dim);
}

.chat-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  color: var(--text-primary);
  font-family: var(--font-sans);
  font-size: 14.5px;
  line-height: 1.6;
  resize: none;
  max-height: 160px;
  padding: 4px 0;
}
.chat-input::placeholder {
  color: var(--text-muted);
}
.chat-input:disabled {
  opacity: 0.6;
}

.btn-send,
.btn-stop {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-in-out);
}

.btn-send {
  background: var(--accent);
  color: white;
}
.btn-send:hover:not(:disabled) {
  background: #3d5bef;
}
.btn-send:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.btn-stop {
  background: var(--bg-hover);
  color: var(--text-secondary);
}
.btn-stop:hover {
  background: var(--border-light);
  color: var(--text-primary);
}

.input-hint {
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 8px;
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 100;
    box-shadow: var(--shadow-lg);
  }
  .sidebar.collapsed {
    width: 0;
    border-right: none;
  }
  .sidebar.collapsed .sidebar-header {
    display: none;
  }

  .message-row {
    padding: 10px 12px;
  }

  .msg-bubble {
    padding: 10px 14px;
    font-size: 14px;
  }

  .input-area {
    padding: 8px 12px 12px;
  }

  .welcome-heading {
    font-size: 20px;
  }
}
</style>
