/**
 * scanX Documentation JavaScript
 * Live log streaming, theme toggle, UI interactions
 */

(function() {
  'use strict';

  // =====================================================================
  // Theme Toggle
  // =====================================================================
  const THEME_KEY = 'sx-docs-theme';

  function applyTheme(theme) {
    if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
    localStorage.setItem(THEME_KEY, theme);
  }

  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initial = saved || (prefersDark ? 'dark' : 'light');
    applyTheme(initial);
  }

  function setupThemeToggle(toggle) {
    if (!toggle) return;
    toggle.addEventListener('click', () => {
      const isLight = document.documentElement.getAttribute('data-theme') === 'light';
      applyTheme(isLight ? 'dark' : 'light');
    });
  }

  // Initialize theme
  initTheme();

  // =====================================================================
  // Table of Contents - Auto-generate from headings
  // =====================================================================
  function buildTOC() {
    const tocList = document.getElementById('tocList');
    if (!tocList) return;

    const sections = document.querySelectorAll('.docs-section[id]');
    const headings = Array.from(sections).map(section => {
      const heading = section.querySelector('h2');
      if (!heading) return null;
      return {
        id: section.id,
        text: heading.textContent.trim(),
        level: 2
      };
    }).filter(Boolean);

    // Also include h3 within sections for deeper TOC
    document.querySelectorAll('.docs-section .section-content h3').forEach(h3 => {
      const section = h3.closest('.docs-section');
      if (section && section.id) {
        headings.push({
          id: section.id + '-' + h3.textContent.trim().toLowerCase().replace(/\s+/g, '-'),
          text: h3.textContent.trim(),
          level: 3,
          parentId: section.id
        });
        // Add id to h3 for scrolling
        if (!h3.id) {
          h3.id = section.id + '-' + h3.textContent.trim().toLowerCase().replace(/\s+/g, '-');
        }
      }
    });

    tocList.innerHTML = headings.map(h => `
      <li class="toc-item toc-level-${h.level}">
        <a href="#${h.id}" class="toc-link" data-section="${h.id}">${h.text}</a>
      </li>
    `).join('');

    // Highlight active section on scroll
    const tocLinks = tocList.querySelectorAll('.toc-link');
    const sectionElements = Array.from(sections).map(s => s.id).filter(Boolean);

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          tocLinks.forEach(link => {
            link.classList.toggle('active', link.dataset.section === entry.target.id);
          });
        }
      });
    }, { rootMargin: '-80px 0px -60% 0px', threshold: 0 });

    sections.forEach(section => observer.observe(section));
  }

  // =====================================================================
  // Smooth Scroll for Anchor Links
  // =====================================================================
  function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        const target = document.querySelector(targetId);
        if (target) {
          e.preventDefault();
          const headerHeight = document.querySelector('.docs-header')?.offsetHeight || 64;
          const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 16;
          window.scrollTo({ top: targetPosition, behavior: 'smooth' });
          history.pushState(null, null, targetId);
        }
      });
    });
  }

  // =====================================================================
  // Search Functionality
  // =====================================================================
  function initSearch() {
    const searchInput = document.getElementById('docs-search');
    const searchResults = document.getElementById('search-results');
    if (!searchInput || !searchResults) return;

    // Build search index from page content
    let searchIndex = [];
    document.querySelectorAll('.docs-section').forEach(section => {
      const heading = section.querySelector('h2');
      const content = section.querySelector('.section-content');
      if (heading && content) {
        searchIndex.push({
          title: heading.textContent.trim(),
          anchor: section.id,
          content: content.textContent.trim().slice(0, 500),
          element: section
        });
      }
      // Also index h3 headings
      content?.querySelectorAll('h3').forEach(h3 => {
        searchIndex.push({
          title: h3.textContent.trim(),
          anchor: h3.id || section.id,
          content: h3.nextElementSibling?.textContent?.trim().slice(0, 300) || '',
          element: h3
        });
      });
    });

    let debounceTimer;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        const query = e.target.value.toLowerCase().trim();
        if (query.length < 2) {
          searchResults.style.display = 'none';
          return;
        }

        const results = searchIndex.filter(item =>
          item.title.toLowerCase().includes(query) ||
          item.content.toLowerCase().includes(query)
        ).slice(0, 8);

        if (results.length) {
          searchResults.innerHTML = results.map(r => `
            <a href="#${r.anchor}" class="search-result-item" role="option">
              <span class="search-result-title">${highlightMatch(r.title, query)}</span>
              <span class="search-result-preview">${highlightMatch(r.content, query)}...</span>
            </a>
          `).join('');
          searchResults.style.display = 'block';
        } else {
          searchResults.innerHTML = '<div class="search-no-results">No results found</div>';
          searchResults.style.display = 'block';
        }
      }, 150);
    });

    searchInput.addEventListener('focus', () => {
      if (searchInput.value.trim().length >= 2) {
        searchResults.style.display = 'block';
      }
    });

    document.addEventListener('click', (e) => {
      if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
        searchResults.style.display = 'none';
      }
    });

    // Keyboard navigation
    searchInput.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        searchResults.style.display = 'none';
        searchInput.blur();
      }
    });
  }

  function highlightMatch(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  }

  // =====================================================================
  // Export Dropdown
  // =====================================================================
  function initExportDropdown() {
    const exportTrigger = document.querySelector('.export-trigger');
    const exportMenu = document.querySelector('.export-menu');
    if (!exportTrigger || !exportMenu) return;

    exportTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      const expanded = exportTrigger.getAttribute('aria-expanded') === 'true';
      exportTrigger.setAttribute('aria-expanded', !expanded);
      exportMenu.setAttribute('aria-hidden', expanded);
    });

    document.addEventListener('click', () => {
      exportTrigger.setAttribute('aria-expanded', 'false');
      exportMenu.setAttribute('aria-hidden', 'true');
    });
  }

  // =====================================================================
  // Mobile TOC Toggle
  // =====================================================================
  function initMobileTOC() {
    const mobileTocBtn = document.getElementById('mobileTocBtn');
    const tocSidebar = document.getElementById('tocSidebar');
    if (!mobileTocBtn || !tocSidebar) return;

    mobileTocBtn.addEventListener('click', () => {
      const expanded = mobileTocBtn.getAttribute('aria-expanded') === 'true';
      mobileTocBtn.setAttribute('aria-expanded', !expanded);
      tocSidebar.classList.toggle('open');
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!tocSidebar.contains(e.target) && !mobileTocBtn.contains(e.target)) {
        tocSidebar.classList.remove('open');
        mobileTocBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // =====================================================================
  // TOC Collapse/Expand
  // =====================================================================
  function initTOCToggle() {
    const tocToggle = document.getElementById('tocToggle');
    const tocList = document.getElementById('tocList');
    if (!tocToggle || !tocList) return;

    tocToggle.addEventListener('click', () => {
      const expanded = tocToggle.getAttribute('aria-expanded') === 'true';
      tocToggle.setAttribute('aria-expanded', !expanded);
      tocList.style.display = expanded ? 'none' : 'block';
    });
  }

  // =====================================================================
  // Mermaid Re-render (for dynamic content)
  // =====================================================================
  function initMermaid() {
    if (typeof mermaid !== 'undefined') {
      mermaid.init(undefined, document.querySelectorAll('.mermaid'));
    }
  }

  // =====================================================================
  // Copy Code Blocks
  // =====================================================================
  function initCodeCopy() {
    document.querySelectorAll('pre code').forEach(codeBlock => {
      const pre = codeBlock.parentElement;
      if (pre.querySelector('.copy-code-btn')) return;

      const btn = document.createElement('button');
      btn.className = 'copy-code-btn';
      btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
      btn.title = 'Copy code';
      btn.style.cssText = `
        position: absolute;
        top: 8px;
        right: 8px;
        padding: 6px;
        background: var(--sx-surface);
        border: 1px solid var(--sx-border);
        border-radius: var(--sx-radius-sm);
        color: var(--sx-text-tertiary);
        cursor: pointer;
        opacity: 0;
        transition: opacity var(--sx-transition), color var(--sx-transition);
      `;
      pre.style.position = 'relative';
      pre.appendChild(btn);

      pre.addEventListener('mouseenter', () => btn.style.opacity = '1');
      pre.addEventListener('mouseleave', () => btn.style.opacity = '0');

      btn.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(codeBlock.textContent);
          btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>';
          btn.style.color = 'var(--sx-success)';
          setTimeout(() => {
            btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>';
            btn.style.color = '';
          }, 2000);
        } catch (e) {
          console.error('Copy failed:', e);
        }
      });
    });
  }

  // =====================================================================
  // Keyboard Shortcuts
  // =====================================================================
  function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + K: Focus search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('docs-search');
        if (searchInput) searchInput.focus();
      }
      // Escape: Close mobile TOC, search results, export menu
      if (e.key === 'Escape') {
        document.getElementById('tocSidebar')?.classList.remove('open');
        document.getElementById('mobileTocBtn')?.setAttribute('aria-expanded', 'false');
        document.getElementById('search-results')?.style.display = 'none';
        const exportTrigger = document.querySelector('.export-trigger');
        if (exportTrigger) {
          exportTrigger.setAttribute('aria-expanded', 'false');
          document.querySelector('.export-menu')?.setAttribute('aria-hidden', 'true');
        }
      }
    });
  }

  // =====================================================================
  // Intersection Observer for Animations
  // =====================================================================
  function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.docs-section, .feature-card, .team-card, .tech-category, .roadmap-column');
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -50px 0px', threshold: 0.1 });

    animatedElements.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      observer.observe(el);
    });
  }

  // =====================================================================
  // Initialize on DOM Ready
  // =====================================================================
  document.addEventListener('DOMContentLoaded', () => {
    buildTOC();
    initSmoothScroll();
    initSearch();
    initExportDropdown();
    initMobileTOC();
    initTOCToggle();
    initMermaid();
    initCodeCopy();
    initKeyboardShortcuts();
    initScrollAnimations();
  });

  // Re-run TOC and Mermaid on view mode change (if using AJAX)
  window.addEventListener('popstate', () => {
    setTimeout(() => {
      buildTOC();
      initMermaid();
      initCodeCopy();
    }, 100);
  });

  // Expose for external use
  window.scanXDocs = {
    buildTOC,
    initMermaid,
    initSearch
  };

})();