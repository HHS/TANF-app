// /components/mobile-navigation.js
class MobileNav extends HTMLElement {
  connectedCallback() {
    fetch('components/mobile-navigation.html')
      .then(res => res.text())
      .then(html => {
        this.innerHTML = html;
        
  // Highlight current page
        const currentPath = window.location.pathname;
        const links = this.querySelectorAll('a');

        links.forEach(link => {
          const linkPath = new URL(link.href).pathname;
          if (linkPath === currentPath) {
            link.classList.add('usa-current');
            link.setAttribute('aria-current', 'page');
          }
        });
      })

      .catch(err => {
        this.innerHTML = '<p>Error loading navigation.</p>';
        console.error('Nav load error:', err);
      });
  }
}

customElements.define('mobile-nav', MobileNav);