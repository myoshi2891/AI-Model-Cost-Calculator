(async function() {
  if (document.getElementById('common-header')) return;

  // await 後は document.currentScript が null になるため事前キャプチャ
  const selfScript = document.currentScript;

  const currentPath = window.location.pathname.split('/').pop() || 'index.html';

  const nav = document.createElement('nav');
  nav.id = 'common-header';
  nav.className = 'ch-nav';
  nav.setAttribute('aria-label', 'Main Navigation');

  const container = document.createElement('div');
  container.className = 'ch-container';
  nav.appendChild(container);

  const brand = document.createElement('a');
  brand.className = 'ch-brand';
  brand.href = './index.html';
  brand.textContent = 'AI Model Pricing';
  container.appendChild(brand);

  const hamburger = document.createElement('button');
  hamburger.className = 'ch-hamburger';
  hamburger.setAttribute('aria-controls', 'ch-menu');
  hamburger.setAttribute('aria-label', 'Toggle menu');
  hamburger.setAttribute('aria-expanded', 'false');
  hamburger.innerHTML = `
    <span class="ch-bar"></span>
    <span class="ch-bar"></span>
    <span class="ch-bar"></span>
  `;
  container.appendChild(hamburger);

  const linksList = document.createElement('ul');
  linksList.id = 'ch-menu';
  linksList.className = 'ch-links';
  
  let links = [];
  const defaultLinks = [
    { name: 'Home', href: './index.html' },
    { name: 'Claude', href: './claude_spec.html' },
    { name: 'Codex', href: './codex_spec.html' },
    { name: 'Gemini', href: './gemini_spec.html' },
    { name: 'Copilot', href: './copilot_spec.html' },
  ];

  // href が安全なプロトコルかを検証（javascript: 等を排除）
  const isSafeHref = (href) => {
    if (typeof href !== 'string') return false;
    if (href.startsWith('/') || href.startsWith('./')) return true;
    try {
      const url = new URL(href, window.location.origin);
      return url.protocol === 'https:' || url.protocol === 'http:';
    } catch {
      return false;
    }
  };

  const isValidLink = (l) => l && l.name && l.href && isSafeHref(l.href);

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

  links.forEach(link => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = link.href;
    a.textContent = link.name;
    const linkPath = link.href.replace('./', '');
    if (currentPath === linkPath) {
      a.className = 'ch-active';
      a.setAttribute('aria-current', 'page');
    }
    li.appendChild(a);
    linksList.appendChild(li);
  });

  const ghLi = document.createElement('li');
  const ghA = document.createElement('a');
  ghA.href = 'https://github.com/myoshi2891/AI-Model-Cost-Calculator';
  ghA.target = '_blank';
  ghA.rel = 'noopener noreferrer';
  ghA.textContent = 'GitHub ↗';
  ghLi.appendChild(ghA);
  linksList.appendChild(ghLi);

  container.appendChild(linksList);

  function handleKeyDown(e) {
    if (e.key === 'Escape') {
      closeMenu();
    }
  }

  function handleOutsideClick(e) {
    if (!linksList.contains(e.target) && !hamburger.contains(e.target)) {
      closeMenu();
    }
  }

  function openMenu() {
    linksList.classList.add('ch-open');
    hamburger.classList.add('ch-open');
    hamburger.setAttribute('aria-expanded', 'true');
    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('click', handleOutsideClick);
  }

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
  document.body.classList.add('has-common-header');
})();
