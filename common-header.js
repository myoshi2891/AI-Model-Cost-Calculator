(async function() {
  if (document.getElementById('common-header')) return;

  // await 後は document.currentScript が null になるため事前キャプチャ
  const selfScript = document.currentScript;

  const pathname = window.location.pathname;

  // 絶対パスの末尾でアクティブページを判定
  const isActivePath = (href) => pathname.endsWith(href) || pathname === href;

  // ドロップダウン親がアクティブか判定（子のいずれかがアクティブなら親もアクティブ）
  const isParentActive = (item) => {
    if (!item.children) return false;
    return item.children.some((child) => isActivePath(child.href));
  };

  const nav = document.createElement('nav');
  nav.id = 'common-header';
  nav.className = 'ch-nav';
  nav.setAttribute('aria-label', 'Main Navigation');

  const container = document.createElement('div');
  container.className = 'ch-container';
  nav.appendChild(container);

  const brand = document.createElement('a');
  brand.className = 'ch-brand';
  brand.href = '/index.html';
  brand.textContent = 'AI Model Pricing';
  container.appendChild(brand);

  const hamburger = document.createElement('button');
  hamburger.className = 'ch-hamburger';
  hamburger.setAttribute('aria-controls', 'ch-menu');
  hamburger.setAttribute('aria-label', 'Toggle menu');
  hamburger.setAttribute('aria-expanded', 'false');
  // DOM メソッドでハンバーガーバーを構築（XSS 安全）
  for (let i = 0; i < 3; i++) {
    const bar = document.createElement('span');
    bar.className = 'ch-bar';
    hamburger.appendChild(bar);
  }
  container.appendChild(hamburger);

  const linksList = document.createElement('ul');
  linksList.id = 'ch-menu';
  linksList.className = 'ch-links';

  let links = [];
  const defaultLinks = [
    { name: 'Home', href: '/index.html' },
    { name: 'Claude', children: [
      { name: 'Skill', href: '/claude/skill.html' },
      { name: 'Agent', href: '/claude/agent.html' },
    ]},
    { name: 'Gemini', children: [
      { name: 'Skill', href: '/gemini/skill.html' },
      { name: 'Agent', href: '/gemini/agent.html' },
    ]},
    { name: 'Codex', children: [
      { name: 'Skill', href: '/codex/skill.html' },
      { name: 'Agent', href: '/codex/agent.html' },
    ]},
    { name: 'Copilot', children: [
      { name: 'Skill', href: '/copilot/skill.html' },
      { name: 'Agent', href: '/copilot/agent.html' },
    ]},
  ];

  // href が安全なプロトコルかを検証（javascript: 等を排除）
  const isSafeHref = (href) => {
    if (typeof href !== 'string') return false;
    if (href.startsWith('//')) return false; // プロトコル相対URL拒否
    if (href.startsWith('/') || href.startsWith('./')) return true;
    try {
      const url = new URL(href, window.location.origin);
      return url.protocol === 'https:' || url.protocol === 'http:';
    } catch {
      return false;
    }
  };

  // フラットリンクとドロップダウン（children付き）の両方をバリデーション
  const isValidLink = (l) => {
    if (!l || !l.name) return false;
    if (l.children) {
      return Array.isArray(l.children) && l.children.every((c) => c && c.name && c.href && isSafeHref(c.href));
    }
    return l.href && isSafeHref(l.href);
  };

  try {
    const res = await fetch('/nav-links.json');
    if (res.ok) {
      const parsed = await res.json();
      if (Array.isArray(parsed) && parsed.every(isValidLink)) {
        links = parsed;
      }
    }
  } catch (e) {
    // ignore fetch/parse errors
  }

  if (links.length === 0) {
    const dataLinks = selfScript ? selfScript.getAttribute('data-links') : null;
    if (dataLinks) {
      try {
        const parsed = JSON.parse(dataLinks);
        if (Array.isArray(parsed) && parsed.every(isValidLink)) {
          links = parsed;
        }
      } catch (e) {
        // ignore parse error
      }
    }
  }

  if (links.length === 0) {
    links = defaultLinks;
  }

  // 全ドロップダウンを閉じるユーティリティ
  function closeAllDropdowns() {
    linksList.querySelectorAll('.ch-dropdown-open').forEach((el) => {
      el.classList.remove('ch-dropdown-open');
      const toggle = el.querySelector('.ch-dropdown-toggle');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    });
  }

  links.forEach((link) => {
    const li = document.createElement('li');

    if (link.children) {
      // ドロップダウン付きリンク
      li.className = 'ch-dropdown';

      const toggle = document.createElement('button');
      toggle.className = 'ch-dropdown-toggle';
      toggle.setAttribute('aria-expanded', 'false');
      toggle.setAttribute('aria-haspopup', 'true');

      const label = document.createElement('span');
      label.textContent = link.name;
      toggle.appendChild(label);

      const arrow = document.createElement('span');
      arrow.className = 'ch-arrow';
      arrow.textContent = ' \u25BE';
      toggle.appendChild(arrow);

      if (isParentActive(link)) {
        toggle.classList.add('ch-active');
      }

      const submenu = document.createElement('ul');
      submenu.className = 'ch-submenu';

      link.children.forEach((child) => {
        const subLi = document.createElement('li');
        const a = document.createElement('a');
        a.href = child.href;
        a.textContent = child.name;
        if (isActivePath(child.href)) {
          a.className = 'ch-active';
          a.setAttribute('aria-current', 'page');
        }
        subLi.appendChild(a);
        submenu.appendChild(subLi);
      });

      // モバイル: click トグルでドロップダウン開閉
      toggle.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = li.classList.contains('ch-dropdown-open');
        closeAllDropdowns();
        if (!isOpen) {
          li.classList.add('ch-dropdown-open');
          toggle.setAttribute('aria-expanded', 'true');
        }
      });

      li.appendChild(toggle);
      li.appendChild(submenu);
    } else {
      // 通常のフラットリンク (Home)
      const a = document.createElement('a');
      a.href = link.href;
      a.textContent = link.name;
      if (isActivePath(link.href)) {
        a.className = 'ch-active';
        a.setAttribute('aria-current', 'page');
      }
      li.appendChild(a);
    }

    linksList.appendChild(li);
  });

  const ghLi = document.createElement('li');
  const ghA = document.createElement('a');
  ghA.href = 'https://github.com/myoshi2891/AI-Model-Cost-Calculator';
  ghA.target = '_blank';
  ghA.rel = 'noopener noreferrer';
  ghA.textContent = 'GitHub \u2197';
  ghLi.appendChild(ghA);
  linksList.appendChild(ghLi);

  container.appendChild(linksList);

  /**
   * Close the navigation menu when the Escape key is pressed.
   * @param {KeyboardEvent} e - The keydown event to inspect for the Escape key.
   */
  function handleKeyDown(e) {
    if (e.key === 'Escape') {
      closeAllDropdowns();
      closeMenu();
    }
  }

  /**
   * Close the navigation menu when the user clicks outside the menu list and hamburger control.
   * @param {Event} e - The click event to evaluate; if its target is not inside the menu or hamburger, the menu is closed.
   */
  function handleOutsideClick(e) {
    if (!linksList.contains(e.target) && !hamburger.contains(e.target)) {
      closeAllDropdowns();
      closeMenu();
    }
  }

  /**
   * Open the collapsible navigation menu and enable outside-click and Escape-to-close behavior.
   */
  function openMenu() {
    linksList.classList.add('ch-open');
    hamburger.classList.add('ch-open');
    hamburger.setAttribute('aria-expanded', 'true');
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('click', handleOutsideClick);
  }

  /**
   * Close the collapsible navigation menu and restore its closed state.
   */
  function closeMenu() {
    linksList.classList.remove('ch-open');
    hamburger.classList.remove('ch-open');
    hamburger.setAttribute('aria-expanded', 'false');
    document.removeEventListener('keydown', handleKeyDown);
    document.removeEventListener('click', handleOutsideClick);
    hamburger.focus();
  }

  hamburger.addEventListener('click', (e) => {
    e.stopPropagation(); // prevent outside click from immediately firing
    const isOpen = linksList.classList.contains('ch-open');
    if (isOpen) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  // Inject as the first child of body to avoid overlapping where possible depending on context
  document.body.insertBefore(nav, document.body.firstChild);

  // ── Disclaimer Banner ──
  const disclaimer = document.createElement('div');
  disclaimer.className = 'ch-disclaimer';
  disclaimer.lang = 'ja';
  const line1 = document.createElement('span');
  line1.className = 'ch-disclaimer-line';
  line1.textContent = '\u26A0 本サイトは個人開発の参考用に作成したものです。必ず各社公式ページで最新の料金をご確認ください。';
  const line2 = document.createElement('span');
  line2.className = 'ch-disclaimer-line';
  line2.textContent = '情報の正確性は保証しません。本サイトの利用による損害等について一切の責任を負いません。';
  disclaimer.appendChild(line1);
  disclaimer.appendChild(line2);
  nav.insertAdjacentElement('afterend', disclaimer);

  /**
   * Synchronizes the rendered height of the disclaimer element into a CSS custom property.
   *
   * Reads the disclaimer element's current layout height and sets the `--ch-disclaimer-height`
   * custom property on the document root to that height in pixels.
   */
  function syncDisclaimerHeight() {
    const h = disclaimer.getBoundingClientRect().height;
    document.documentElement.style.setProperty('--ch-disclaimer-height', h + 'px');
  }

  if (typeof ResizeObserver !== 'undefined') {
    const ro = new ResizeObserver(syncDisclaimerHeight);
    ro.observe(disclaimer);
  } else {
    // ResizeObserver 未対応ブラウザ向けフォールバック
    requestAnimationFrame(syncDisclaimerHeight);
    window.addEventListener('resize', syncDisclaimerHeight);
  }

  document.body.classList.add('has-common-header');
})();
