class SiteFooter extends HTMLElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.render();
    }

    render() {
        this.innerHTML = `
        <footer class="site-footer" style="background: #130f40; color: #ffffff; padding: 4rem 2rem; margin-top: 4rem;">
            <div class="container" style="max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 3rem;">
                
                <!-- Company Info -->
                <div class="footer-section">
                    <h3 style="color: #f0932b; margin-bottom: 1.5rem; font-size: 1.2rem; text-transform: uppercase; letter-spacing: 1px;">Orbis Local</h3>
                    <p style="line-height: 1.6; color: rgba(255,255,255,0.8);">Advanced Generative Engine Optimization (GEO) and AI Search Visibility solutions for modern businesses.</p>
                    <div style="margin-top: 2rem;">
                        <p style="margin-bottom: 0.5rem;"><strong style="color: #f0932b;">Tel:</strong> +1 888 546 5819</p>
                        <p style="margin-bottom: 0.5rem;"><strong style="color: #f0932b;">Email:</strong> insights@myorbislocal.com</p>
                        <p><strong style="color: #f0932b;">Address:</strong> 716 W. Washington St</p>
                    </div>
                </div>

                <!-- EEAT Resources -->
                <div class="footer-section">
                    <h3 style="color: #f0932b; margin-bottom: 1.5rem; font-size: 1.2rem; text-transform: uppercase; letter-spacing: 1px;">EEAT Principles</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin-bottom: 0.8rem;"><a href="experience.html" style="color: rgba(255,255,255,0.8); text-decoration: none; transition: color 0.3s;">Experience</a></li>
                        <li style="margin-bottom: 0.8rem;"><a href="expertise.html" style="color: rgba(255,255,255,0.8); text-decoration: none; transition: color 0.3s;">Expertise</a></li>
                        <li style="margin-bottom: 0.8rem;"><a href="authoritativeness.html" style="color: rgba(255,255,255,0.8); text-decoration: none; transition: color 0.3s;">Authoritativeness</a></li>
                        <li style="margin-bottom: 0.8rem;"><a href="trustworthiness.html" style="color: rgba(255,255,255,0.8); text-decoration: none; transition: color 0.3s;">Trustworthiness</a></li>
                    </ul>
                </div>

                <!-- Dashboard Links -->
                <div class="footer-section">
                    <h3 style="color: #f0932b; margin-bottom: 1.5rem; font-size: 1.2rem; text-transform: uppercase; letter-spacing: 1px;">Quick Links</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin-bottom: 0.8rem;"><a href="/" style="color: rgba(255,255,255,0.8); text-decoration: none;">Dashboard Home</a></li>
                        <li style="margin-bottom: 0.8rem;"><a href="case-studio.html" style="color: rgba(255,255,255,0.8); text-decoration: none;">Case Studio</a></li>
                        <li style="margin-bottom: 0.8rem;"><a href="documentation.html" style="color: rgba(255,255,255,0.8); text-decoration: none;">Documentation</a></li>
                    </ul>
                </div>

            </div>
            <div class="footer-bottom" style="max-width: 1200px; margin: 3rem auto 0; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 2rem; text-align: center; color: rgba(255,255,255,0.5); font-size: 0.9rem;">
                <p>&copy; 2026 Orbis Local. All rights reserved. Optimized for Generative Engines.</p>
            </div>
        </footer>
        `;
    }
}

customElements.define('site-footer', SiteFooter);
