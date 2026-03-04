class SiteHeader extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        // Simple logic to set 'active' class based on current path
        const currentPath = window.location.pathname;
        const page = currentPath.split('/').pop() || 'index.html';

        this.innerHTML = `
            <header class="site-header">
                <nav class="main-nav">
                    <ul>
                        <li><a href="index.html" class="${page === 'index.html' || page === 'home.html' ? 'active' : ''}">Home</a></li>
                        <li><a href="case-studio.html" class="${page === 'case-studio.html' ? 'active' : ''}">Case Studio</a></li>
                        <li><a href="more-orbis.html" class="${page === 'more-orbis.html' ? 'active' : ''}">More Orbis</a></li>
                        <li><a href="documentation.html" class="${page === 'documentation.html' ? 'active' : ''}">Documentation</a></li>
                    </ul>
                </nav>
                <div class="header-top">
                    <div class="logo">ORBIS LOCAL</div>
                    <div class="tagline">Enterprise AI Search Visibility Auditor</div>
                </div>
            </header>
            <button id="backToTop" class="back-to-top" aria-label="Back to Top">
                <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="18 15 12 9 6 15"></polyline>
                </svg>
            </button>
        `;

        // Add event listener for back to top after it's added to DOM
        const backToTopBtn = this.querySelector('#backToTop');
        if (backToTopBtn) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 300) {
                    backToTopBtn.classList.add('visible');
                } else {
                    backToTopBtn.classList.remove('visible');
                }
            });

            backToTopBtn.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    }
}

customElements.define('site-header', SiteHeader);
