(function() {
  if (document.getElementById('common-header')) return;

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
  hamburger.setAttribute('aria-label', 'Toggle menu');
  hamburger.setAttribute('aria-expanded', 'false');
  hamburger.innerHTML = `
    <span class="ch-bar"></span>
    <span class="ch-bar"></span>
    <span class="ch-bar"></span>
  `;
  container.appendChild(hamburger);

  const linksList = document.createElement('ul');
  linksList.className = 'ch-links';
  
  const links = [
    { name: 'Home', href: './index.html' },
    { name: 'Claude', href: './claude_spec.html' },
    { name: 'Codex', href: './codex_spec.html' },
    { name: 'Gemini', href: './gemini_spec.html' },
    { name: 'Copilot', href: './copilot_spec.html' },
  ];

  links.forEach(link => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = link.href;
    a.textContent = link.name;
    const linkPath = link.href.replace('./', '');
    if (currentPath === linkPath || (currentPath === '' && linkPath === 'index.html')) {
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

  hamburger.addEventListener('click', () => {
    const isOpen = linksList.classList.toggle('ch-open');
    hamburger.classList.toggle('ch-open');
    hamburger.setAttribute('aria-expanded', isOpen);
  });

  // Inject as the first child of body to avoid overlapping where possible depending on context
  document.body.insertBefore(nav, document.body.firstChild);
})();
