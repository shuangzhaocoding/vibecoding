<template>
  <footer class="site-footer">
    <div class="site-footer-inner">
      <div class="footer-grid">
        <section class="footer-col">
          <h3>{{ t('footer.aboutTitle') }}</h3>
          <p>{{ t('footer.aboutDesc') }}</p>
        </section>
        <section class="footer-col">
          <h3>{{ t('footer.linksTitle') }}</h3>
          <ul class="friend-links">
            <li v-for="link in friendLinks" :key="link.url">
              <a :href="link.url" target="_blank" rel="noopener noreferrer">{{ link.name }}</a>
            </li>
          </ul>
        </section>
        <section class="footer-col">
          <h3>{{ t('footer.contactTitle') }}</h3>
          <p>{{ t('footer.contactDesc') }}</p>
        </section>
      </div>
      <div class="footer-beian">
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">
          {{ t('footer.beian') }}
        </a>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const friendLinks = [
  { name: 'Cursor', url: 'https://cursor.com' },
  { name: 'GitHub', url: 'https://github.com' },
  { name: 'OpenTiny', url: 'https://opentiny.design' },
  { name: 'Hugging Face', url: 'https://huggingface.co' },
  { name: 'Vercel', url: 'https://vercel.com' },
]
</script>

<style scoped>
.site-footer {
  margin-top: auto;
  border-top: 1px solid var(--border);
  background: var(--bg-elevated);
}

.site-footer-inner {
  max-width: 1120px;
  margin: 0 auto;
  padding: 36px 24px 20px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr;
  gap: 28px 32px;
}

.footer-col h3 {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.footer-col p {
  margin: 0;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.friend-links {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.friend-links a {
  font-size: 13px;
  color: var(--text-secondary);
  transition: color 0.15s ease;
}

.friend-links a:hover {
  color: var(--primary);
}

.footer-beian {
  margin-top: 28px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
  text-align: center;
}

.footer-beian a {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 0.02em;
}

.footer-beian a:hover {
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .site-footer-inner {
    padding: 28px 16px 18px;
  }

  .footer-grid {
    grid-template-columns: 1fr;
    gap: 22px;
  }
}
</style>
